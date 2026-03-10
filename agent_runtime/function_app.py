# agent_runtime/function_app.py

import azure.functions as func
import logging
import json
import time

# Import our custom logic
from src.migrationmind_agents.persistence.mysql_repo import MySQLRepository
from src.migrationmind_agents.contracts import (
    SurveyorOutput, ArchitectOutput, AccountantOutput, RiskOfficerOutput
)

app = func.FunctionApp()

@app.service_bus_queue_trigger(
    arg_name="msg", 
    queue_name="assessment-jobs", 
    connection="SERVICE_BUS_CONNECTION_STRING"
)
def assessment_orchestrator(msg: func.ServiceBusMessage):
    """
    Triggered by Django to run the 4-Agent Pipeline.
    """
    body = msg.get_body().decode('utf-8')
    logging.info(f"\n{'='*50}\n[Orchestrator] ServiceBus trigger received: {body}\n{'='*50}")
    
    # Instantiate the DB repo inside the function so environment variables are loaded
    db_repo = MySQLRepository()
    
    try:
        payload = json.loads(body)
        assessment_id = payload.get("assessment_id")
        is_demo = payload.get("is_demo", False)
        
        if not assessment_id:
            logging.error("[Orchestrator] No assessment_id provided in message.")
            return

        # Tell Django UI we are processing
        db_repo.update_assessment_status(assessment_id, "processing")
        
        # ---------------------------------------------------------
        # AGENT PIPELINE EXECUTION (Simulated delays for UI testing)
        # ---------------------------------------------------------
        
        # 1. Surveyor Agent
        logging.info(f"[Agent: Surveyor] Analyzing network flow logs for {assessment_id}...")
        time.sleep(2)
        db_repo.save_agent_run(assessment_id, "Surveyor", "success", "Identified 6 apps and 7 dependencies via Azure MCP.")
        
        # 2. Architect Agent
        logging.info(f"[Agent: Architect] Performing topological sort for {assessment_id}...")
        time.sleep(3)
        db_repo.save_agent_run(assessment_id, "Architect", "success", "Created 3 migration waves.")
        
        # 3. Accountant Agent
        logging.info(f"[Agent: Accountant] Querying Azure Retail Prices API for {assessment_id}...")
        time.sleep(2)
        db_repo.save_agent_run(assessment_id, "Accountant", "success", "Calculated $6,130/mo savings.")
        
        # 4. Risk Officer Agent
        logging.info(f"[Agent: Risk Officer] Evaluating GDPR/HIPAA deterministic rules for {assessment_id}...")
        time.sleep(2)
        db_repo.save_agent_run(assessment_id, "Risk Officer", "success", "Flagged 1 Blocking Risk (GDPR) and 1 Warning (Downtime).")
        
        # ---------------------------------------------------------
        # PIPELINE COMPLETE
        # ---------------------------------------------------------
        
        logging.info(f"[Orchestrator] All agents completed successfully for {assessment_id}.")
        db_repo.update_assessment_status(assessment_id, "playbook_ready")
        
    except Exception as e:
        logging.error(f"[Orchestrator] FATAL ERROR processing message: {str(e)}")
        try:
            if 'assessment_id' in locals() and assessment_id:
                db_repo.update_assessment_status(assessment_id, "failed")
        except:
            pass
