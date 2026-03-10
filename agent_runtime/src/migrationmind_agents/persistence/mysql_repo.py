# agent_runtime/src/migrationmind_agents/persistence/mysql_repo.py

import os
import json
import logging
import urllib.parse
import pymysql

logger = logging.getLogger(__name__)

class MySQLRepository:
    def __init__(self):
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set in local.settings.json")
        
        db_url = db_url.strip("'\"")
        parsed = urllib.parse.urlparse(db_url)
        self.host = parsed.hostname
        self.port = parsed.port or 3306
        self.user = urllib.parse.unquote(parsed.username) if parsed.username else ""
        self.password = urllib.parse.unquote(parsed.password) if parsed.password else ""
        self.database = parsed.path.lstrip('/')

    def get_connection(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )

    def update_assessment_status(self, assessment_id: str, status: str):
        logger.info(f"[DB] Updating Assessment {assessment_id} to status: {status}")
        query = "UPDATE core_assessment SET status = %s WHERE id = %s"
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (status, assessment_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"[DB] Failed to update assessment status: {str(e)}")
            return False

    def save_agent_run(self, assessment_id: str, agent_name: str, status: str, logs: str):
        logger.info(f"[DB] Saving AgentRun audit for {agent_name}")
        query = """
            INSERT INTO core_agentrun 
            (assessment_id, agent_name, status, logs, tokens_in, tokens_out, duration_ms, model_used, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (assessment_id, agent_name, status, logs, 0, 0, 0, "gpt-4o"))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"[DB] Failed to save agent run: {str(e)}")

    def save_playbook_version(self, assessment_id: str, payload_dict: dict):
        """Saves the final compiled JSON playbook into the database."""
        logger.info(f"[DB] Saving new Playbook Version for {assessment_id}")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 1. Calculate next version number for this assessment
            cursor.execute("SELECT COALESCE(MAX(version_number), 0) + 1 FROM core_playbookversion WHERE assessment_id = %s", (assessment_id,))
            next_version = cursor.fetchone()[0]
            
            # 2. Insert the JSON payload
            query = """
                INSERT INTO core_playbookversion 
                (assessment_id, version_number, payload, diff_summary, created_at) 
                VALUES (%s, %s, %s, %s, NOW())
            """
            # Convert python dictionary to JSON string for the DB
            cursor.execute(query, (assessment_id, next_version, json.dumps(payload_dict), "Agent pipeline generation"))
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"[DB] Successfully saved Playbook v{next_version} for {assessment_id}")
            return True
        except Exception as e:
            logger.error(f"[DB] Failed to save playbook version: {str(e)}")
            return False
