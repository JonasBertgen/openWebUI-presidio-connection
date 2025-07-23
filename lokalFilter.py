from pydantic import BaseModel, Field
from typing import Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

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

    def inlet(
        self,
        body: dict,
    ) -> dict:
        try:

            # self.logger("inlet")
            self.logger.info("inlet")
            message = body["messages"][-1]["content"]
            analyzer = AnalyzerEngine()

            # Call analyzer to get results
            results = analyzer.analyze(
                text=message, entities=["PHONE_NUMBER", "PERSON"], language="en"
            )
            self.logger.info("reached result")
            # Analyzer results are passed to the AnonymizerEngine for anonymization
            anonymizer = AnonymizerEngine()
            anonymized_text = anonymizer.anonymize(
                text=message, analyzer_results=results
            )
            self.logger.info(anonymized_text)
            body["messages"][-1]["content"] = anonymized_text.text
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
