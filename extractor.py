# extractor.py
import json
from ollama import chat

from pydantic import BaseModel, validator

class ActionItem(BaseModel):
    title: str


    priority: str
    assignee: str
    details: str

    @validator('priority')
    def check_priority(cls, v):
        allowed_priorities = ["High", "Med", "Low"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of {allowed_priorities}")
        return v

class ExtractionResult(BaseModel):
    summary: str
    action_items: list[ActionItem]
    client_email: str







def process_transcript(transcript_text: str, model_name: str = "qwen2.5-coder:7b") -> ExtractionResult:





    system_prompt = """
    You are a senior technical project manager. Please parse the following transcript for developer action items, technical context, and draft a client follow-up email.

    Transcript:
    {transcript_text}

    Structure your response in JSON format using the following schema:
    {
        "summary": "A brief summary of the key points.",
        "action_items": [
            {
                "title": "Task Title",
                "priority": "High/Med/Low",
                "assignee": "Dev/Client/Unassigned",
                "details": "Detailed context for the task."
            }
        ],







        "client_email": "Draft a follow-up email to be sent to the client."
    }
    """

    result = ollama.chat(prompt=system_prompt.format(transcript_text=transcript_text), model=model_name, format=ExtractionResult.model_json_schema())
    return ExtractionResult.parse_raw(result)
# Quick Test
if __name__ == "__main__":
    sample_txt = "[0.0s] Dev: We need to fix the OAuth bug on /api/login before Friday. Client: Okay, I will send over the API keys."
    result = process_transcript(sample_txt)
    print(json.dumps(result.model_dump(), indent=2))