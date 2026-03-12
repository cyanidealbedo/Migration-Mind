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
        self.host     = parsed.hostname
        self.port     = parsed.port or 3306
        self.user     = urllib.parse.unquote(parsed.username) if parsed.username else ""
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

    # ── Assessment ──────────────────────────────────────────────────────────

    def update_assessment_status(self, assessment_id: str, status: str) -> bool:
        logger.info(f"[DB] Assessment {assessment_id} → {status}")
        try:
            conn = self.get_connection()
            cur  = conn.cursor()
            cur.execute(
                "UPDATE core_assessment SET status = %s WHERE id = %s",
                (status, assessment_id)
            )
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"[DB] update_assessment_status failed: {e}")
            return False

    # ── Agent Runs ───────────────────────────────────────────────────────────

    def save_agent_run(
        self,
        assessment_id: str,
        agent_name:    str,
        status:        str,
        logs:          str,
        duration_ms:   int = 0,
        tokens_in:     int = 0,
        tokens_out:    int = 0,
        model_used:    str = "gpt-4o"
    ) -> bool:
        logger.info(f"[DB] Saving AgentRun: {agent_name} ({status}) — {duration_ms}ms")
        query = """
            INSERT INTO core_agentrun
            (assessment_id, agent_name, status, logs, tokens_in, tokens_out, duration_ms, model_used, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        try:
            conn = self.get_connection()
            cur  = conn.cursor()
            cur.execute(query, (
                assessment_id, agent_name, status, logs[:4000],
                tokens_in, tokens_out, duration_ms, model_used
            ))
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"[DB] save_agent_run failed: {e}")
            return False

    # ── Playbook Versions ────────────────────────────────────────────────────

    def save_playbook_version(
        self,
        assessment_id: str,
        payload_dict:  dict,
        diff_summary:  str = ""
    ) -> bool:
        logger.info(f"[DB] Saving PlaybookVersion for {assessment_id}")
        try:
            conn = self.get_connection()
            cur  = conn.cursor()

            cur.execute(
                "SELECT COALESCE(MAX(version_number), 0) + 1 "
                "FROM core_playbookversion WHERE assessment_id = %s",
                (assessment_id,)
            )
            next_version = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO core_playbookversion
                (assessment_id, version_number, payload, diff_summary, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (assessment_id, next_version, json.dumps(payload_dict), diff_summary)
            )
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"[DB] Saved Playbook v{next_version} for {assessment_id}. Diff: {diff_summary[:80]}")
            return True
        except Exception as e:
            logger.error(f"[DB] save_playbook_version failed: {e}")
            return False

    # ── Risk Card Sign-off ───────────────────────────────────────────────────

    def sign_off_risk(self, risk_id: int, signed_by: str) -> bool:
        try:
            conn = self.get_connection()
            cur  = conn.cursor()
            cur.execute(
                "UPDATE core_riskcard SET signed_off_by = %s, signed_off_at = NOW() WHERE id = %s",
                (signed_by, risk_id)
            )
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"[DB] sign_off_risk failed: {e}")
            return False
