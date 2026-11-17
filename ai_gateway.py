"""Optional Gemini narrative, not a project approval or funding decision."""
import json
from pydantic import BaseModel, Field

class AIReview(BaseModel):
    summary: str = Field(min_length=10)
    missing_evidence: list[str]
    suggested_verification_questions: list[str]
    limitations: list[str]

def explain(assessment: dict, api_key: str, model: str = 'gemini-2.5-flash') -> AIReview:
    if not api_key.strip():
        raise ValueError('GEMINI_API_KEY is not configured')
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)
    result = client.models.generate_content(
        model=model,
        contents=json.dumps(assessment),
        config=types.GenerateContentConfig(
            system_instruction=('Only describe documentation gaps in the supplied SYNTHETIC educational project. '
                'Do not invent evidence, assert actual implementation feasibility, investment readiness, '
                'funding eligibility, safety, effectiveness, or climate impact. '
                'Provide concrete questions for a human reviewer.'),
            response_mime_type='application/json', response_schema=AIReview, temperature=0))
    if not result.text:
        raise ValueError('Empty model response')
    return AIReview.model_validate_json(result.text)
