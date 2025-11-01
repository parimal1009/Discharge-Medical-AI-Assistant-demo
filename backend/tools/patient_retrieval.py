"""
Patient Retrieval Tool
LangChain tool for retrieving patient discharge reports
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
from backend.database.patient_db import PatientDatabase
from backend.utils.logger import system_logger

class PatientRetrievalInput(BaseModel):
    """Input schema for patient retrieval tool"""
    patient_name: str = Field(
        description="Full name or partial name of the patient to retrieve"
    )

class PatientRetrievalTool(BaseTool):
    """Tool for retrieving patient discharge reports from database"""
    
    name: str = "patient_retrieval"
    description: str = (
        "Retrieve patient discharge reports by patient name. "
        "Use this tool to get detailed information about a patient's "
        "discharge diagnosis, medications, dietary restrictions, "
        "follow-up instructions, and warning signs. "
        "Input should be the patient's full name or last name."
    )
    args_schema: Type[BaseModel] = PatientRetrievalInput
    
    patient_db: PatientDatabase = Field(default=None, exclude=True)
    
    def __init__(self, patient_db: PatientDatabase):
        super().__init__(patient_db=patient_db)
    
    def _run(self, patient_name: str) -> str:
        """Synchronous execution of patient retrieval"""
        try:
            # Retrieve patient data
            patient_data = self.patient_db.get_patient(patient_name)
            
            if not patient_data:
                system_logger.log_tool_usage(
                    "patient_retrieval",
                    patient_name,
                    "Patient not found",
                    False
                )
                return (
                    f"No patient found with name: {patient_name}. "
                    f"Please check the spelling or try using just the last name."
                )
            
            # Format the patient data in a readable way
            formatted_report = f"""
PATIENT DISCHARGE REPORT FOUND:

Patient Name: {patient_data['patient_name']}
Discharge Date: {patient_data['discharge_date']}

PRIMARY DIAGNOSIS:
{patient_data['primary_diagnosis']}

MEDICATIONS:
{self._format_list(patient_data['medications'])}

DIETARY RESTRICTIONS:
{patient_data['dietary_restrictions']}

FOLLOW-UP APPOINTMENTS:
{patient_data['follow_up']}

WARNING SIGNS TO WATCH FOR:
{patient_data['warning_signs']}

DISCHARGE INSTRUCTIONS:
{patient_data['discharge_instructions']}

---
This discharge report can be used to answer patient questions and provide personalized care guidance.
"""
            
            system_logger.log_tool_usage(
                "patient_retrieval",
                patient_name,
                f"Successfully retrieved data for {patient_data['patient_name']}",
                True
            )
            
            return formatted_report
            
        except Exception as e:
            error_msg = f"Error retrieving patient data: {str(e)}"
            system_logger.log_error("patient_retrieval_tool", error_msg)
            system_logger.log_tool_usage(
                "patient_retrieval",
                patient_name,
                error_msg,
                False
            )
            return f"Unable to retrieve patient data due to system error. Please try again."
    
    async def _arun(self, patient_name: str) -> str:
        """Asynchronous execution (delegates to sync)"""
        return self._run(patient_name)
    
    def _format_list(self, items: list) -> str:
        """Format list items with bullet points"""
        return "\n".join([f"  • {item}" for item in items])
