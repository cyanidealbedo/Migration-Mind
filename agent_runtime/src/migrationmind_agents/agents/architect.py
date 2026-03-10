# agent_runtime/src/migrationmind_agents/agents/architect.py

import os
import logging
from openai import AzureOpenAI
from ..contracts import ArchitectOutput

logger = logging.getLogger(__name__)

class ArchitectAgent:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        )
        self.deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    def run(self, dependency_graph: dict) -> ArchitectOutput:
        logger.info("[Architect] Requesting wave plan from Azure OpenAI...")

        system_prompt = """
        You are the Architect Agent for an Azure Migration.
        Your job is to analyze the provided dependency graph of an on-premise application environment.
        You must perform a topological sort to group the assets into safe 'Migration Waves'.
        - Core shared services (Active Directory, shared caches) must go in Wave 1.
        - Databases must go in Wave 2.
        - Web applications that depend on those databases must go in Wave 3.
        You MUST return your answer strictly matching the required JSON schema.
        """

        # Using standard chat completions but asking for a JSON response 
        # (In production with the latest SDK, you can use .beta.chat.completions.parse)
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the dependency graph: {dependency_graph}"}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "architect_output",
                    "schema": ArchitectOutput.model_json_schema()
                }
            },
            temperature=0.2
        )

        raw_json = response.choices[0].message.content
        logger.info("[Architect] Successfully generated structured wave plan.")
        
        # Parse the JSON string back into our strict Pydantic model
        return ArchitectOutput.model_validate_json(raw_json)
