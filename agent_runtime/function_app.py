# agent_runtime/function_app.py

import azure.functions as func
import logging
import json
import time

from src.migrationmind_agents.persistence.mysql_repo import MySQLRepository
from src.migrationmind_agents.agents.architect import ArchitectAgent
from src.migrationmind_agents.agents.accountant import AccountantAgent

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
        
        # 1. Surveyor Agent
        logging.info(f"[Agent: Surveyor] Mocking network flow logs for {assessment_id}...")
        mock_dependency_graph = {
            "Web-IIS-01":["Prod-SQL-01", "Auth-Redis-01"],
            "Web-IIS-02":["Prod-SQL-01", "Auth-Redis-01"],
            "Prod-SQL-01":["AD-DC-Primary"],
            "Auth-Redis-01":[],
            "AD-DC-Primary":[]
        }
        time.sleep(1)
        db_repo.save_agent_run(assessment_id, "Surveyor", "success", "Identified 5 apps.")

        # 2. Architect Agent
        logging.info(f"[Agent: Architect] Performing topological sort via LLM...")
        architect = ArchitectAgent()
        architect_result = architect.run(mock_dependency_graph)
        db_repo.save_agent_run(assessment_id, "Architect", "success", architect_result.summary)
        
        # 3. Accountant Agent
        logging.info(f"[Agent: Accountant] Querying Azure Retail Prices API...")
        accountant = AccountantAgent()
        accountant_result = accountant.run(architect_result.waves)
        db_repo.save_agent_run(assessment_id, "Accountant", "success", accountant_result.summary)
        
        # 4. Risk Officer
        logging.info(f"[Agent: Risk Officer] Evaluating rules...")
        time.sleep(1)
        db_repo.save_agent_run(assessment_id, "Risk Officer", "success", "Checked rules.")
        
        # 5. COMPILE AND SAVE THE LIVING PLAYBOOK
        logging.info(f"[Orchestrator] Compiling final playbook JSON...")
        playbook_payload = {
            "dependency_graph": mock_dependency_graph,
            "architect": architect_result.model_dump(),  # Convert Pydantic object to dict
            "accountant": accountant_result.model_dump(), # Convert Pydantic object to dict
            "risk":[] # Mocks for now
        }
        db_repo.save_playbook_version(assessment_id, playbook_payload)

        # 6. Finish
        logging.info(f"[Orchestrator] All agents completed successfully for {assessment_id}.")
        db_repo.update_assessment_status(assessment_id, "playbook_ready")
        
    except Exception as e:
        logging.error(f"[Orchestrator] FATAL ERROR processing message: {str(e)}")
        try:
            if 'assessment_id' in locals() and assessment_id:
                db_repo.update_assessment_status(assessment_id, "failed")
        except:
            pass
