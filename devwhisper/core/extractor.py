"""Ollama structured information extraction for meetings."""
import json
import ollama
from .models import ExtractionResult


def process_transcript(
    transcript_text: str,
    model_name: str = "qwen2.5-coder:7b",
) -> ExtractionResult:
    """Extract structured meeting data from a transcript using local Ollama."""
    system_prompt = (
        "You are an experienced technical project lead and engineering manager. "
        "Analyze the following meeting transcript to extract high-priority technical decisions, "
        "developer action items (with priority High/Med/Low and assignee Dev/Client/Unassigned), "
        "a concise summary, and a professional client follow-up email in markdown."
    )

    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Transcript:\n{transcript_text}"},
        ],
        format=ExtractionResult.model_json_schema(),
    )

    content = response.message.content
    return ExtractionResult.model_validate_json(content)

