"""Deterministic, educational assessment of documentation readiness."""
from __future__ import annotations
import hashlib
import json
from pydantic import BaseModel, Field, model_validator

CRITERIA = {
    'problem_definition': 'Problem and baseline defined',
    'evidence': 'Supporting evidence documented',
    'stakeholders': 'Stakeholders and inclusion documented',
    'governance': 'Accountable owner identified',
    'budget': 'Indicative budget documented',
    'funding': 'Funding pathway documented',
    'timeline': 'Milestones and schedule documented',
    'indicators': 'Measurable monitoring indicators defined',
    'risks': 'Risks and mitigations documented',
    'maintenance': 'Operations and maintenance plan documented',
}
STATES = ('documented', 'partial', 'missing')
WEIGHTS = {'documented': 1.0, 'partial': 0.5, 'missing': 0.0}

class Project(BaseModel):
    id: str
    name: str
    sector: str
    description: str
    source_type: str = 'synthetic'
    criteria: dict[str, str]
    evidence_notes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode='after')
    def check_criteria(self):
        if set(self.criteria) != set(CRITERIA):
            raise ValueError('Exactly the ten documented criteria are required')
        if any(v not in STATES for v in self.criteria.values()):
            raise ValueError('Unknown readiness status')
        if self.source_type != 'synthetic':
            raise ValueError('This educational dataset accepts synthetic projects only')
        return self

def assess(project: Project) -> dict:
    counts = {state: sum(v == state for v in project.criteria.values()) for state in STATES}
    score = round(100 * sum(WEIGHTS[v] for v in project.criteria.values()) / len(CRITERIA), 1)
    gaps = [CRITERIA[k] for k, v in project.criteria.items() if v != 'documented']
    return {'project_id': project.id, 'project': project.name, 'sector': project.sector,
            'documentation_score_pct': score, **counts, 'gaps': gaps,
            'status': 'Documentation complete for this checklist' if not gaps else 'Documentation gaps identified'}

def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
