# agent_runtime/src/migrationmind_agents/agents/risk_officer.py

import os
import logging
from openai import AzureOpenAI
from ..contracts import RiskOfficerOutput

logger = logging.getLogger(__name__)

class RiskOfficerAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        )
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    def run(self, architect_waves_json: str) -> RiskOfficerOutput:
        logger.info("[Risk Officer] Requesting compliance evaluation from Azure OpenAI...")

        system_prompt = """
        You are the Risk Officer Agent for an Azure Migration.
        Your job is to analyze the provided migration wave plan and flag any compliance, security, or downtime risks.
        - Look for Databases (SQL) and flag potential downtime SLAs or GDPR data sovereignty risks.
        - Look for Authentication/Cache services and flag security/networking risks.
        - If a wave looks safe, you do not need to create a risk card for it.
        You MUST return your answer strictly matching the required JSON schema for RiskOfficerOutput.
        """

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please evaluate this wave plan: {architect_waves_json}"}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "risk_officer_output",
                    "schema": RiskOfficerOutput.model_json_schema()
                }
            },
            temperature=0.3
        )

        raw_json = response.choices[0].message.content
        logger.info(f"[Risk Officer] Successfully generated structured risk cards: {raw_json}")
        
        # Parse the JSON string back into our strict Pydantic model
        return RiskOfficerOutput.model_validate_json(raw_json)
