# extractor.py
import json
from ollama import chat
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    title: str
    priority: str = Field(description="High, Medium, or Low")
    assignee: str = Field(description="Developer, Client, or Unassigned")
    details: str

class ExtractionResult(BaseModel):
    summary: str
    action_items: list[ActionItem]
    client_email: str

SYSTEM_PROMPT = """
You are a senior technical project manager. Analyze the meeting transcript provided by the user.
Extract all developer action items, technical requirements, bug fixes, and draft a professional client follow-up email summarizing what was agreed upon.
Return output strictly in JSON matching the requested schema.
"""

def process_transcript(transcript_text: str, model_name: str = "qwen2.5-coder:7b") -> ExtractionResult:
    response = chat(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n{transcript_text}"}
        ],
        format=ExtractionResult.model_json_schema(), # Enforces JSON schema
        options={"temperature": 0.2}
    )
    
    raw_json = response.message.content
    return ExtractionResult.model_validate_json(raw_json)

# Quick Test
if __name__ == "__main__":
    sample_txt = "[0.0s] Dev: We need to fix the OAuth bug on /api/login before Friday. Client: Okay, I will send over the API keys."
    result = process_transcript(sample_txt)
    print(json.dumps(result.model_dump(), indent=2))