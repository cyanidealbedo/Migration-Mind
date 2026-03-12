# agent_runtime/function_app.py
import azure.functions as func
import logging
import json
import time
import os

from src.migrationmind_agents.persistence.mysql_repo import MySQLRepository
from src.migrationmind_agents.agents.architect import ArchitectAgent
from src.migrationmind_agents.agents.accountant import AccountantAgent
from src.migrationmind_agents.agents.risk_officer import RiskOfficerAgent

# ── OpenTelemetry instrumentation ──
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace

    _conn_str = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if _conn_str:
        configure_azure_monitor(connection_string=_conn_str)
        logging.info("✅ App Insights / OpenTelemetry configured in Function runtime")
    tracer = trace.get_tracer("migrationmind.orchestrator")
except Exception as _e:
    logging.warning(f"OTel setup skipped: {_e}")
    # Stub tracer so code paths still work without telemetry
    class _NoopSpan:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def set_attribute(self, *a): pass
        def record_exception(self, *a): pass
        def set_status(self, *a): pass

    class _NoopTracer:
        def start_as_current_span(self, *a, **kw): return _NoopSpan()

    tracer = _NoopTracer()

app = func.FunctionApp()


def _build_diff_summary(old_payload: dict | None, new_payload: dict) -> str:
    """Generate a human-readable diff summary between two playbook versions."""
    if not old_payload:
        waves = new_payload.get('architect', {}).get('waves', [])
        assets = sum(len(w.get('assets', [])) for w in waves)
        costs = new_payload.get('accountant', {}).get('per_wave_costs', [])
        savings = sum(c.get('estimated_savings', 0) for c in costs)
        return (
            f"Initial playbook generated. "
            f"{len(waves)} migration waves · {assets} assets · "
            f"${savings:,.2f}/mo estimated savings."
        )

    old_waves = old_payload.get('architect', {}).get('waves', [])
    new_waves = new_payload.get('architect', {}).get('waves', [])
    old_assets = sum(len(w.get('assets', [])) for w in old_waves)
    new_assets = sum(len(w.get('assets', [])) for w in new_waves)
    removed = old_assets - new_assets

    old_costs = old_payload.get('accountant', {}).get('per_wave_costs', [])
    new_costs = new_payload.get('accountant', {}).get('per_wave_costs', [])
    old_savings = sum(c.get('estimated_savings', 0) for c in old_costs)
    new_savings = sum(c.get('estimated_savings', 0) for c in new_costs)
    savings_delta = new_savings - old_savings

    old_risks = len(old_payload.get('risk', {}).get('wave_risk_cards', []))
    new_risks = len(new_payload.get('risk', {}).get('wave_risk_cards', []))

    parts = []
    if removed > 0:
        parts.append(f"{removed} assets removed (wave completed)")
    if len(new_waves) != len(old_waves):
        parts.append(f"waves updated: {len(old_waves)} → {len(new_waves)}")
    if abs(savings_delta) > 1:
        direction = "increased" if savings_delta > 0 else "decreased"
        parts.append(f"monthly savings {direction} by ${abs(savings_delta):,.2f}")
    if new_risks != old_risks:
        parts.append(f"risk cards updated: {old_risks} → {new_risks}")

    return "Playbook recalculated. " + " · ".join(parts) if parts else "Playbook recalculated."


@app.service_bus_queue_trigger(
    arg_name="msg",
    queue_name="assessment-jobs",
    connection="SERVICE_BUS_CONNECTION_STRING"
)
def assessment_orchestrator(msg: func.ServiceBusMessage):
    body = msg.get_body().decode('utf-8')
    logging.info(f"\n{'='*50}\n[Orchestrator] Triggered: {body}\n{'='*50}")

    db_repo = MySQLRepository()

    with tracer.start_as_current_span("orchestrator.run") as root_span:
        try:
            payload = json.loads(body)
            assessment_id = payload.get("assessment_id")
            root_span.set_attribute("assessment_id", assessment_id)

            db_repo.update_assessment_status(assessment_id, "processing")

            # Determine version and fetch previous payload for diff
            # NOTE: Two separate queries — MySQL ONLY_FULL_GROUP_BY rejects
            # mixing COUNT(*) with non-aggregated columns in one SELECT.
            conn = db_repo.get_connection()
            cursor = conn.cursor()

            # Query 1: how many versions exist?
            cursor.execute(
                "SELECT COUNT(*) FROM core_playbookversion WHERE assessment_id = %s",
                (assessment_id,)
            )
            version_count = cursor.fetchone()[0]

            # Query 2: fetch the latest payload for diff summary
            prev_payload = None
            if version_count > 0:
                cursor.execute(
                    "SELECT payload FROM core_playbookversion "
                    "WHERE assessment_id = %s ORDER BY version_number DESC LIMIT 1",
                    (assessment_id,)
                )
                prev_row = cursor.fetchone()
                if prev_row and prev_row[0]:
                    try:
                        prev_payload = json.loads(prev_row[0])
                    except Exception:
                        prev_payload = None

            cursor.close()
            conn.close()

            is_recalculation = version_count > 0
            root_span.set_attribute("is_recalculation", is_recalculation)
            root_span.set_attribute("version_number", version_count + 1)

            # ── Agent 1: Surveyor ──
            with tracer.start_as_current_span("surveyor.run") as span:
                t0 = time.time()
                span.set_attribute("assessment_id", assessment_id)
                logging.info(f"[Agent: Surveyor] Building dependency graph for {assessment_id}...")

                dependency_graph = {
                    "Web-IIS-01":    ["Prod-SQL-01", "Auth-Redis-01"],
                    "Web-IIS-02":    ["Prod-SQL-01", "Auth-Redis-01"],
                    "Prod-SQL-01":   ["AD-DC-Primary"],
                    "Auth-Redis-01": [],
                    "AD-DC-Primary": []
                }

                if is_recalculation:
                    logging.info("[Surveyor] Removing completed Wave 1 assets from graph.")
                    for k in ["Auth-Redis-01", "AD-DC-Primary"]:
                        dependency_graph.pop(k, None)
                    for k in dependency_graph:
                        dependency_graph[k] = [
                            d for d in dependency_graph[k]
                            if d not in ("Auth-Redis-01", "AD-DC-Primary")
                        ]

                ms = int((time.time() - t0) * 1000)
                span.set_attribute("duration_ms", ms)
                db_repo.save_agent_run(
                    assessment_id, "Surveyor", "success",
                    f"Built dependency graph with {len(dependency_graph)} nodes.",
                    duration_ms=ms
                )

            # ── Agent 2: Architect ──
            with tracer.start_as_current_span("architect.run") as span:
                t0 = time.time()
                span.set_attribute("assessment_id", assessment_id)
                logging.info(f"[Agent: Architect] Requesting wave plan from Azure OpenAI...")
                architect = ArchitectAgent()
                architect_result = architect.run(dependency_graph)
                ms = int((time.time() - t0) * 1000)
                span.set_attribute("duration_ms", ms)
                span.set_attribute("waves_generated", architect_result.total_waves)
                db_repo.save_agent_run(
                    assessment_id, "Architect", "success",
                    architect_result.summary,
                    duration_ms=ms,
                    tokens_in=getattr(architect_result, '_tokens_in', 0),
                    tokens_out=getattr(architect_result, '_tokens_out', 0),
                    model_used=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
                )

            # ── Agent 3: Accountant ──
            with tracer.start_as_current_span("accountant.run") as span:
                t0 = time.time()
                span.set_attribute("assessment_id", assessment_id)
                logging.info(f"[Agent: Accountant] Querying Azure Retail Prices API...")
                accountant = AccountantAgent()
                accountant_result = accountant.run(architect_result.waves)
                ms = int((time.time() - t0) * 1000)
                span.set_attribute("duration_ms", ms)
                span.set_attribute("monthly_savings", float(
                    accountant_result.total_business_case.three_year_npv
                ))
                db_repo.save_agent_run(
                    assessment_id, "Accountant", "success",
                    accountant_result.summary,
                    duration_ms=ms
                )

            # ── Agent 4: Risk Officer ──
            with tracer.start_as_current_span("risk_officer.run") as span:
                t0 = time.time()
                span.set_attribute("assessment_id", assessment_id)
                logging.info(f"[Agent: Risk Officer] Evaluating compliance rules...")
                risk_officer = RiskOfficerAgent()
                risk_result = risk_officer.run(architect_result.model_dump_json())
                ms = int((time.time() - t0) * 1000)
                span.set_attribute("duration_ms", ms)
                span.set_attribute("risk_cards_generated", len(risk_result.wave_risk_cards))
                db_repo.save_agent_run(
                    assessment_id, "Risk Officer", "success",
                    f"Generated {len(risk_result.wave_risk_cards)} risk cards.",
                    duration_ms=ms,
                    model_used=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
                )

            # ── Compile playbook ──
            with tracer.start_as_current_span("playbook.compile") as span:
                new_payload = {
                    "dependency_graph": dependency_graph,
                    "architect":        architect_result.model_dump(),
                    "accountant":       accountant_result.model_dump(),
                    "risk":             risk_result.model_dump(),
                }
                diff = _build_diff_summary(prev_payload, new_payload)
                root_span.set_attribute("diff_summary", diff)
                logging.info(f"[Orchestrator] Diff: {diff}")

                db_repo.save_playbook_version(assessment_id, new_payload, diff_summary=diff)
                db_repo.update_assessment_status(assessment_id, "playbook_ready")
                span.set_attribute("version_saved", version_count + 1)

            logging.info(f"[Orchestrator] ✅ Playbook v{version_count + 1} saved for {assessment_id}.")

        except Exception as e:
            logging.error(f"[Orchestrator] FATAL ERROR: {str(e)}", exc_info=True)
            root_span.record_exception(e)
            try:
                if 'assessment_id' in locals() and assessment_id:
                    db_repo.update_assessment_status(assessment_id, "failed")
            except Exception:
                pass
