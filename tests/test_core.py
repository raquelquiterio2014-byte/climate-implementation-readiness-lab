import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from core import CRITERIA, Project, assess, fingerprint
from storage import save_review, list_reviews
from ai_gateway import AIReview, explain

DATA=json.loads((Path(__file__).resolve().parents[1]/'data/projects.json').read_text())
def project(n): return Project.model_validate(DATA[n])
def test_three_projects(): assert len(DATA)==3
def test_ten_criteria(): assert len(CRITERIA)==10
def test_all_synthetic(): assert all(x['source_type']=='synthetic' for x in DATA)
def test_water_score(): assert assess(project(0))['documentation_score_pct']==65.0
def test_energy_score(): assert assess(project(1))['documentation_score_pct']==85.0
def test_city_score(): assert assess(project(2))['documentation_score_pct']==45.0
def test_water_missing(): assert assess(project(0))['missing']==2
def test_energy_missing(): assert assess(project(1))['missing']==0
def test_city_missing(): assert assess(project(2))['missing']==4
def test_gaps_are_human_labels(): assert 'Funding pathway documented' in assess(project(0))['gaps']
def test_all_documented():
    p=project(0).model_copy(update={'criteria':dict.fromkeys(CRITERIA,'documented')})
    assert assess(p)['documentation_score_pct']==100
    assert assess(p)['gaps']==[]
def test_all_missing():
    p=project(0).model_copy(update={'criteria':dict.fromkeys(CRITERIA,'missing')})
    assert assess(p)['documentation_score_pct']==0
def test_reject_unknown_status():
    x=dict(DATA[0]); x['criteria']={**x['criteria'],'funding':'approved'}
    with pytest.raises(ValidationError): Project.model_validate(x)
def test_reject_missing_criterion():
    x=dict(DATA[0]); x['criteria']={k:v for k,v in x['criteria'].items() if k!='funding'}
    with pytest.raises(ValidationError): Project.model_validate(x)
def test_reject_real_source():
    x={**DATA[0],'source_type':'real'}
    with pytest.raises(ValidationError): Project.model_validate(x)
def test_hash_deterministic(): assert fingerprint({'b':2,'a':1})==fingerprint({'a':1,'b':2})
def test_review_saved(tmp_path):
    a=assess(project(0)); db=tmp_path/'review.sqlite'
    save_review(db,a['project_id'],'Reviewer','reviewed','Checked the gaps',a,{'summary':'Example'})
    assert list_reviews(db)[0]['project_id']==a['project_id']
def test_review_project_mismatch(tmp_path):
    with pytest.raises(ValueError): save_review(tmp_path/'x.sqlite','wrong','Reviewer','reviewed','Enough detail',assess(project(0)),{})
def test_invalid_decision(tmp_path):
    a=assess(project(0))
    with pytest.raises(ValueError): save_review(tmp_path/'x.sqlite',a['project_id'],'Reviewer','approved','Enough detail',a,{})
def test_missing_key():
    with pytest.raises(ValueError): explain({},'')
def test_ai_schema():
    a=AIReview(summary='Synthetic documentation only.',missing_evidence=[],suggested_verification_questions=[],limitations=[])
    assert 'Synthetic' in a.summary
