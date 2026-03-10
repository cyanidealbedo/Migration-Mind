# agent_runtime/src/migrationmind_agents/persistence/mysql_repo.py

import os
import logging
import urllib.parse
import pymysql  # Switched to pure-Python PyMySQL for zero-dependency execution

logger = logging.getLogger(__name__)

class MySQLRepository:
    def __init__(self):
        # Parse the DATABASE_URL exactly as Django does it
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set in local.settings.json")
        
        # Safely strip any accidental single or double quotes from the URL
        db_url = db_url.strip("'\"")
        
        parsed = urllib.parse.urlparse(db_url)
        self.host = parsed.hostname
        self.port = parsed.port or 3306
        self.user = urllib.parse.unquote(parsed.username) if parsed.username else ""
        self.password = urllib.parse.unquote(parsed.password) if parsed.password else ""
        self.database = parsed.path.lstrip('/')

    def get_connection(self):
        """Creates and returns a new MySQL database connection."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4'
        )

    def update_assessment_status(self, assessment_id: str, status: str):
        """Updates the status in the core_assessment table (Django)."""
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
        """Saves an audit trail record of the agent execution."""
        logger.info(f"[DB] Saving AgentRun audit for {agent_name} (Assessment: {assessment_id})")
        
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
