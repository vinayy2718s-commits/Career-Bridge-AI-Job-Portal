import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean(x): return re.sub(r"[^a-z0-9+#. ]"," ",str(x or "").lower())

def token_set(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]*",str(text or "").lower()))

def similarity(a,b):
    if not a.strip() or not b.strip(): return 0.0
    try:
        v=TfidfVectorizer(stop_words="english").fit_transform([clean(a),clean(b)])
        return float(cosine_similarity(v[0:1],v[1:2])[0][0])
    except Exception: return 0.0

def skill_overlap(candidate_skills, required):
    c=token_set(candidate_skills); r=token_set(required)
    if not r:return 0.0
    return len(c & r)/len(r)

def recommend_jobs(profile,jobs):
    profile_text=" ".join(str(profile.get(k,"") or "") for k in ["headline","skills","education","preferences","resume_text"])
    result=[]
    for j in jobs:
        job_text=" ".join(str(j.get(k,"") or "") for k in ["title","description","required_skills","category","location"])
        sim=similarity(profile_text,job_text)
        overlap=skill_overlap(profile.get("skills",""),j.get("required_skills",""))
        exp=float(profile.get("experience_years") or 0)
        req=float(j.get("experience_required") or 0)
        exp_score=1 if exp>=req else (exp/max(req,1))*0.5
        score=round((sim*.55+overlap*.35+exp_score*.10)*100,2)
        x=dict(j); x["match_score"]=score
        result.append(x)
    return sorted(result,key=lambda x:x["match_score"],reverse=True)

def rank_candidates(candidates,job):
    out=[]
    required=job.get("required_skills","")
    reqexp=float(job.get("experience_required") or 0)
    for c in candidates:
        text=c.get("text","")
        sim=similarity(text, job.get("description","")+" "+required)
        overlap=skill_overlap(c.get("skills",""),required)
        exp=float(c.get("experience_years") or 0)
        exp_score=1 if exp>=reqexp else (exp/max(reqexp,1))*0.5
        score=round((sim*.55+overlap*.35+exp_score*.10)*100,2)
        x=dict(c); x["score"]=score
        out.append(x)
    return sorted(out,key=lambda x:x["score"],reverse=True)

def skills_gap(profile,job):
    required=token_set(job.get("required_skills",""))
    current=token_set(profile.get("skills","")+" "+profile.get("resume_text",""))
    missing=sorted(required-current)
    return {"job_title":job.get("title"),"required_skills":sorted(required),"detected_skills":sorted(required & current),
            "missing_skills":missing,
            "learning_recommendations":[f"Learn/practice {s}" for s in missing[:8]]}
