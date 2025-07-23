from pydantic import BaseModel, Field
from typing import Optional
import requests
import logging


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )
        max_turns: int = Field(
            default=8, description="Maximum allowable conversation turns for a user."
        )
        pass

    class UserValves(BaseModel):
        max_turns: int = Field(
            default=4, description="Maximum allowable conversation turns for a user."
        )
        pass

    def __init__(self):
        self.valves = self.Valves()
        self.logger = logging.getLogger(__name__)
        self.logger.info("logger loaded")

        pass

    def getPIIPOS(self, promptInput: str):
        analyze_response = requests.post(
            "http://presidio-analyzer:3000/analyze",
            headers={"Content-Type": "application/json"},
            json={"text": promptInput, "language": "en"},
        )
        return analyze_response.json()

    def anonymizeCall(self, promptInput: str) -> str:
        response = requests.post(
            "http://presidio-anonymizer:3000/anonymize",
            headers={"Content-Type": "application/json"},
            json={
                "text": promptInput,
                "analyzer_results": self.getPIIPOS(promptInput),
                "anonymizers": {
                    "DEFAULT": {"type": "replace", "new_value": "[REDACTED]"}
                },
            },
        )

        return response.json()["text"]

    def inlet(
        self,
        body: dict,
    ) -> dict:
        try:

            self.logger.info("inlet")
            message = body["messages"][-1]["content"]

            anonymizedPrompt = self.anonymizeCall(message)
            self.logger.info(f"Prompt anonymized to {anonymizedPrompt}")
            body["messages"][-1]["content"] = anonymizedPrompt
            self.logger.info("no error in inlet --------")
        except Exception as e:
            self.logger.info("some error in inlet --------")
            self.logger.error(e)

        return body

    def outlet(self, body: dict) -> dict:
        # Modify or analyze the response body after processing by the API.
        # This function is the post-processor for the API, which can be used to modify the response
        # or perform additional checks and analytics.
        self.logger.info("outlet without function")

        return body
