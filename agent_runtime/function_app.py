# agent_runtime/function_app.py

import azure.functions as func
import logging
import json
import time

from src.migrationmind_agents.persistence.mysql_repo import MySQLRepository
from src.migrationmind_agents.agents.architect import ArchitectAgent
from src.migrationmind_agents.agents.accountant import AccountantAgent
from src.migrationmind_agents.agents.risk_officer import RiskOfficerAgent

app = func.FunctionApp()

@app.service_bus_queue_trigger(
    arg_name="msg", 
    queue_name="assessment-jobs", 
    connection="SERVICE_BUS_CONNECTION_STRING"
)
def assessment_orchestrator(msg: func.ServiceBusMessage):
    body = msg.get_body().decode('utf-8')
    logging.info(f"\n{'='*50}\n[Orchestrator] ServiceBus trigger received: {body}\n{'='*50}")
    
    db_repo = MySQLRepository()
    
    try:
        payload = json.loads(body)
        assessment_id = payload.get("assessment_id")
        
        db_repo.update_assessment_status(assessment_id, "processing")
        
        # Check if we are generating v1 or v2+
        conn = db_repo.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM core_playbookversion WHERE assessment_id = %s", (assessment_id,))
        version_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        is_recalculation = version_count > 0
        
        # 1. Surveyor Agent
        logging.info(f"[Agent: Surveyor] Building network flow graph for {assessment_id}...")
        
        dependency_graph = {
            "Web-IIS-01": ["Prod-SQL-01", "Auth-Redis-01"],
            "Web-IIS-02":["Prod-SQL-01", "Auth-Redis-01"],
            "Prod-SQL-01": ["AD-DC-Primary"],
            "Auth-Redis-01": [],
            "AD-DC-Primary":[]
        }
        
        # If this is Version 2, remove the completed Wave 1 assets to simulate a living playbook
        if is_recalculation:
            logging.info("[Agent: Surveyor] Removing completed assets (Auth-Redis-01, AD-DC-Primary) from graph.")
            del dependency_graph["Auth-Redis-01"]
            del dependency_graph["AD-DC-Primary"]
            dependency_graph["Web-IIS-01"].remove("Auth-Redis-01")
            dependency_graph["Web-IIS-02"].remove("Auth-Redis-01")
            dependency_graph["Prod-SQL-01"].remove("AD-DC-Primary")
            
        time.sleep(1)
        db_repo.save_agent_run(assessment_id, "Surveyor", "success", "Updated dependency graph.")

        # 2. Architect Agent
        logging.info(f"[Agent: Architect] Performing topological sort via Azure OpenAI...")
        architect = ArchitectAgent()
        architect_result = architect.run(dependency_graph)
        db_repo.save_agent_run(assessment_id, "Architect", "success", architect_result.summary)
        
        # 3. Accountant Agent
        logging.info(f"[Agent: Accountant] Querying Azure Retail Prices API...")
        accountant = AccountantAgent()
        accountant_result = accountant.run(architect_result.waves)
        db_repo.save_agent_run(assessment_id, "Accountant", "success", accountant_result.summary)
        
        # 4. Risk Officer Agent (REAL AI NOW)
        logging.info(f"[Agent: Risk Officer] Evaluating rules via Azure OpenAI...")
        risk_officer = RiskOfficerAgent()
        risk_result = risk_officer.run(architect_result.model_dump_json())
        db_repo.save_agent_run(assessment_id, "Risk Officer", "success", f"Generated {len(risk_result.wave_risk_cards)} risk cards.")
        
        # 5. COMPILE AND SAVE
        logging.info(f"[Orchestrator] Compiling Playbook Version {version_count + 1} JSON...")
        playbook_payload = {
            "dependency_graph": dependency_graph,
            "architect": architect_result.model_dump(),
            "accountant": accountant_result.model_dump(),
            "risk": risk_result.model_dump() 
        }
        db_repo.save_playbook_version(assessment_id, playbook_payload)

        # 6. Finish
        logging.info(f"[Orchestrator] Playbook updated successfully for {assessment_id}.")
        db_repo.update_assessment_status(assessment_id, "playbook_ready")
        
    except Exception as e:
        logging.error(f"[Orchestrator] FATAL ERROR processing message: {str(e)}")
        try:
            if 'assessment_id' in locals() and assessment_id:
                db_repo.update_assessment_status(assessment_id, "failed")
        except:
            pass
