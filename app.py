"""COP31 AI Solutions Lab | Day 11 — synthetic implementation readiness demo."""
import json
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from core import Project, CRITERIA, assess, fingerprint
from ai_gateway import explain
from storage import save_review, list_reviews

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
PROJECTS = [Project.model_validate(item) for item in json.loads((ROOT/'data/projects.json').read_text(encoding='utf-8'))]
DB = ROOT / 'local_data' / 'reviews.sqlite3'

st.set_page_config(page_title='Climate Implementation Readiness Lab', page_icon='🏗️', layout='wide')
st.markdown('''<style>.stApp{background-color:#091d33;color:#e7f5ff}
[data-testid="stMetric"]{background:#133753;padding:15px;border-radius:12px}</style>''', unsafe_allow_html=True)
st.title('🏗️ Climate Implementation Readiness Lab V1.0')
st.caption('COP31 AI Solutions Lab | Day 11 | November 19, 2026')
st.warning('SYNTHETIC educational scenarios. The checklist measures documentation completeness, NOT technical feasibility, financing eligibility, or investment approval.')
results = [assess(p) for p in PROJECTS]
tabs = st.tabs(['📊 Project Portfolio Overview','🧩 Readiness Assessment','🤖 AI & Human Review','📤 Export & Methodology'])
with tabs[0]:
    st.subheader('Illustrative climate project portfolio')
    a,b,c=st.columns(3)
    a.metric('Synthetic projects',len(PROJECTS))
    b.metric('Assessment criteria',len(CRITERIA))
    c.metric('Mean documentation score',f"{sum(r['documentation_score_pct'] for r in results)/len(results):.1f}%")
    st.dataframe(pd.DataFrame([{k:r[k] for k in ('project','sector','documentation_score_pct','documented','partial','missing')} for r in results]),hide_index=True,use_container_width=True)
    st.bar_chart(pd.DataFrame(results).set_index('project')['documentation_score_pct'])
with tabs[1]:
    st.subheader('Transparent checklist and missing evidence')
    chosen=st.selectbox('Select synthetic project',[p.name for p in PROJECTS],key='project_assessment')
    project=next(p for p in PROJECTS if p.name==chosen)
    report=assess(project)
    st.metric('Documentation score',f"{report['documentation_score_pct']}%")
    st.dataframe(pd.DataFrame([{'Criterion':label,'Status':project.criteria[key],
                               'Illustrative note':project.evidence_notes.get(key,'Not provided')}
                              for key,label in CRITERIA.items()]),hide_index=True,use_container_width=True)
    st.markdown('**Unresolved documentation:**')
    for gap in report['gaps']: st.write('• '+gap)
    if not report['gaps']: st.success('All ten fields documented; independent validation is still required.')
    st.caption('Score = 100 × (documented + 0.5 × partial) / 10. Equal weights are illustrative and not a validated readiness index.')
with tabs[2]:
    st.subheader('Optional AI narrative with human review')
    selected=st.selectbox('Select project for review',[p.name for p in PROJECTS],key='project_review')
    current=next(p for p in PROJECTS if p.name==selected)
    assessment=assess(current)
    st.caption('Generate sends this synthetic assessment to Google Gemini; no personal or real project data is included.')
    if st.button('Generate gap explanation'):
        try:
            with st.spinner('Requesting structured explanation...'):
                response=explain(assessment,os.getenv('GEMINI_API_KEY',''),os.getenv('GEMINI_MODEL','gemini-2.5-flash'))
            st.session_state['ai_result']={'project_id':current.id,'assessment':assessment,'response':response.model_dump()}
        except Exception as exc:
            st.error(f'AI unavailable: {exc}')
    record=st.session_state.get('ai_result')
    if record and record['project_id']==current.id and record['assessment']==assessment:
        st.json(record['response'])
        with st.form('human_review'):
            reviewer=st.text_input('Reviewer role or pseudonym',value='Educational reviewer')
            decision=st.selectbox('Review decision',['needs_revision','reviewed','rejected'])
            rationale=st.text_area('Reason for decision',value='Check evidence gaps and source limitations.')
            if st.form_submit_button('Record human review'):
                try:
                    save_review(DB,current.id,reviewer,decision,rationale,assessment,record['response'])
                    st.success('Review saved locally. This is not a funding approval.')
                except ValueError as exc: st.error(str(exc))
    elif record:
        st.info('The saved AI explanation refers to another project. Generate a new explanation before reviewing this project.')
with tabs[3]:
    st.subheader('Reproducible exports and limitations')
    table=pd.DataFrame([{k:r[k] for k in ('project_id','project','sector','documentation_score_pct','documented','partial','missing','status')} for r in results])
    st.download_button('Download project indicators CSV',table.to_csv(index=False).encode('utf-8'),'implementation_readiness.csv','text/csv')
    reviews=list_reviews(DB)
    st.download_button('Download local review history CSV',pd.DataFrame(reviews,columns=['id','timestamp_utc','project_id','reviewer','decision','rationale','assessment_sha256','ai_sha256']).to_csv(index=False).encode('utf-8'),'review_history.csv','text/csv')
    payload={'data_origin':'synthetic','projects':[p.model_dump() for p in PROJECTS],'assessments':results,'review_history':reviews,'source_sha256':fingerprint([p.model_dump() for p in PROJECTS])}
    st.download_button('Download complete JSON',json.dumps(payload,indent=2,ensure_ascii=False),'implementation_readiness.json','application/json')
    st.markdown('**Methodology:** Ten equally weighted documentation checks; documented = 1, partial = 0.5, missing = 0. Results are descriptive only. A complete checklist is not proof of feasibility or funding eligibility.')
    st.markdown('**Limitations:** Synthetic records; no actual budgets, project permits, stakeholder consultations, climate impacts or official COP31 decisions. Optional AI output can be wrong. Human review is required. SHA-256 fingerprints do not create tamper-proof storage.')
