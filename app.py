import os, re, json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from db import query, execute, init_demo_data
from ai_engine import recommend_jobs, rank_candidates, skills_gap
from resume_parser import parse_resume

load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "career-bridge-development-secret")
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED = {"pdf", "docx"}

def auth_required(role=None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Login required"}), 401
            if role and session.get("role") != role:
                return jsonify({"error": "Access denied"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return deco

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "Career Bridge API"})

@app.post("/api/register")
def register():
    data = request.get_json() or {}
    name, email, password = data.get("name","").strip(), data.get("email","").strip().lower(), data.get("password","")
    role = data.get("role","job_seeker")
    if not name or not email or not password:
        return jsonify({"error":"Name, email and password are required"}), 400
    if role not in ("job_seeker","recruiter"):
        role = "job_seeker"
    try:
        uid = execute("INSERT INTO users(name,email,password_hash,role,phone,location) VALUES(%s,%s,%s,%s,%s,%s)",
                      (name,email,generate_password_hash(password),role,data.get("phone"),data.get("location")))
        if role == "job_seeker":
            execute("INSERT INTO seeker_profiles(user_id,skills) VALUES(%s,%s)", (uid, data.get("skills","")))
        else:
            execute("INSERT INTO recruiter_profiles(user_id,company_name,company_description,company_location) VALUES(%s,%s,%s,%s)",
                    (uid, data.get("company_name") or name, data.get("company_description",""), data.get("location","")))
        return jsonify({"message":"Registration successful","user_id":uid}), 201
    except Exception as e:
        return jsonify({"error":"Email may already be registered","detail":str(e)}), 400

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    user = query("SELECT * FROM users WHERE email=%s", (data.get("email","").strip().lower(),), one=True)
    if not user or not check_password_hash(user["password_hash"], data.get("password","")):
        return jsonify({"error":"Invalid email or password"}), 401
    session["user_id"], session["role"], session["name"] = user["id"], user["role"], user["name"]
    return jsonify({"message":"Login successful","user":safe_user(user)})

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"Logged out"})

@app.get("/api/me")
def me():
    if "user_id" not in session: return jsonify({"user":None})
    u = query("SELECT * FROM users WHERE id=%s",(session["user_id"],),one=True)
    return jsonify({"user":safe_user(u) if u else None})

def safe_user(u):
    return {k:u[k] for k in ("id","name","email","role","phone","location","created_at")}

@app.get("/api/profile")
@auth_required()
def profile():
    u = query("SELECT * FROM users WHERE id=%s",(session["user_id"],),one=True)
    if u["role"]=="job_seeker":
        p=query("SELECT * FROM seeker_profiles WHERE user_id=%s",(u["id"],),one=True)
    elif u["role"]=="recruiter":
        p=query("SELECT * FROM recruiter_profiles WHERE user_id=%s",(u["id"],),one=True)
    else: p={}
    return jsonify({"user":safe_user(u),"profile":p or {}})

@app.put("/api/profile")
@auth_required()
def update_profile():
    d=request.get_json() or {}
    uid=session["user_id"]
    execute("UPDATE users SET name=%s,phone=%s,location=%s WHERE id=%s",(d.get("name"),d.get("phone"),d.get("location"),uid))
    if session["role"]=="job_seeker":
        execute("""UPDATE seeker_profiles SET headline=%s,skills=%s,experience_years=%s,education=%s,preferences=%s
                   WHERE user_id=%s""",(d.get("headline"),d.get("skills",""),d.get("experience_years",0),d.get("education"),d.get("preferences",""),uid))
    elif session["role"]=="recruiter":
        execute("""UPDATE recruiter_profiles SET company_name=%s,company_description=%s,website=%s,company_location=%s
                   WHERE user_id=%s""",(d.get("company_name"),d.get("company_description"),d.get("website"),d.get("company_location"),uid))
    return jsonify({"message":"Profile updated"})

@app.post("/api/resume")
@auth_required("job_seeker")
def upload_resume():
    f=request.files.get("resume")
    if not f: return jsonify({"error":"Choose a resume file"}),400
    ext=f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED: return jsonify({"error":"Only PDF and DOCX are supported"}),400
    filename=f"{session['user_id']}_{secure_filename(f.filename)}"
    path=os.path.join(app.config["UPLOAD_FOLDER"],filename)
    f.save(path)
    text=parse_resume(path)
    execute("UPDATE seeker_profiles SET resume_filename=%s,resume_text=%s WHERE user_id=%s",(filename,text,session["user_id"]))
    return jsonify({"message":"Resume uploaded and parsed","filename":filename,"text_preview":text[:500]})

@app.get("/api/jobs")
def jobs():
    keyword=request.args.get("q","").strip()
    location=request.args.get("location","").strip()
    category=request.args.get("category","").strip()
    sql="""SELECT j.*, rp.company_name FROM jobs j
           JOIN recruiter_profiles rp ON rp.user_id=j.recruiter_id
           WHERE j.status='open'"""
    params=[]
    if keyword:
        sql+=" AND (j.title LIKE %s OR j.description LIKE %s OR j.required_skills LIKE %s)"
        x=f"%{keyword}%"; params += [x,x,x]
    if location:
        sql+=" AND j.location LIKE %s"; params.append(f"%{location}%")
    if category:
        sql+=" AND j.category LIKE %s"; params.append(f"%{category}%")
    sql+=" ORDER BY j.created_at DESC"
    return jsonify({"jobs":query(sql,tuple(params))})

@app.get("/api/jobs/<int:job_id>")
def job_detail(job_id):
    j=query("""SELECT j.*,rp.company_name,rp.company_description,rp.website
               FROM jobs j JOIN recruiter_profiles rp ON rp.user_id=j.recruiter_id WHERE j.id=%s""",(job_id,),one=True)
    if not j:return jsonify({"error":"Job not found"}),404
    return jsonify({"job":j})

@app.post("/api/jobs")
@auth_required("recruiter")
def create_job():
    d=request.get_json() or {}
    required=["title","description","required_skills","location","category"]
    if not all(d.get(k) for k in required): return jsonify({"error":"Fill all required job fields"}),400
    jid=execute("""INSERT INTO jobs(recruiter_id,title,description,required_skills,experience_required,location,category,salary_min,salary_max,job_type)
                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (session["user_id"],d["title"],d["description"],d["required_skills"],d.get("experience_required",0),
         d["location"],d["category"],d.get("salary_min"),d.get("salary_max"),d.get("job_type","Full-time")))
    return jsonify({"message":"Job posted","job_id":jid}),201

@app.get("/api/recruiter/jobs")
@auth_required("recruiter")
def recruiter_jobs():
    return jsonify({"jobs":query("SELECT * FROM jobs WHERE recruiter_id=%s ORDER BY created_at DESC",(session["user_id"],))})

@app.post("/api/jobs/<int:job_id>/apply")
@auth_required("job_seeker")
def apply(job_id):
    j=query("SELECT * FROM jobs WHERE id=%s AND status='open'",(job_id,),one=True)
    if not j:return jsonify({"error":"Job not found"}),404
    p=query("SELECT * FROM seeker_profiles WHERE user_id=%s",(session["user_id"],),one=True) or {}
    candidate_text=(p.get("skills","") or "")+" "+(p.get("resume_text","") or "")+" "+(p.get("education","") or "")
    score=rank_candidates([{"text":candidate_text,"skills":p.get("skills",""),"experience_years":p.get("experience_years",0)}],
                           j)[0]["score"]
    try:
        execute("INSERT INTO applications(job_id,seeker_id,cover_note,match_score) VALUES(%s,%s,%s,%s)",
                (job_id,session["user_id"],(request.get_json() or {}).get("cover_note",""),score))
        execute("INSERT INTO notifications(user_id,title,message) VALUES(%s,%s,%s)",
                (j["recruiter_id"],"New application",f"{session['name']} applied for {j['title']}."))
        return jsonify({"message":"Application submitted","match_score":score}),201
    except Exception:
        return jsonify({"error":"You have already applied for this job"}),400

@app.get("/api/applications")
@auth_required("job_seeker")
def my_applications():
    return jsonify({"applications":query("""SELECT a.*,j.title,rp.company_name FROM applications a
        JOIN jobs j ON j.id=a.job_id JOIN recruiter_profiles rp ON rp.user_id=j.recruiter_id
        WHERE a.seeker_id=%s ORDER BY a.created_at DESC""",(session["user_id"],))})

@app.get("/api/recruiter/applications/<int:job_id>")
@auth_required("recruiter")
def recruiter_applications(job_id):
    j=query("SELECT * FROM jobs WHERE id=%s AND recruiter_id=%s",(job_id,session["user_id"]),one=True)
    if not j:return jsonify({"error":"Job not found"}),404
    rows=query("""SELECT a.*,u.name,u.email,u.location,sp.skills,sp.experience_years,sp.education,sp.resume_text
                  FROM applications a JOIN users u ON u.id=a.seeker_id
                  LEFT JOIN seeker_profiles sp ON sp.user_id=u.id
                  WHERE a.job_id=%s ORDER BY a.match_score DESC""",(job_id,))
    ranked=rank_candidates([{"id":r["id"],"name":r["name"],"text":(r.get("resume_text") or "")+" "+(r.get("skills") or ""),
                             "skills":r.get("skills") or "","experience_years":r.get("experience_years") or 0,
                             "status":r["status"]} for r in rows],j)
    return jsonify({"applications":ranked})

@app.patch("/api/applications/<int:app_id>")
@auth_required("recruiter")
def update_application(app_id):
    d=request.get_json() or {}
    status=d.get("status")
    if status not in ("Applied","Shortlisted","Rejected","Selected"):
        return jsonify({"error":"Invalid status"}),400
    row=query("""SELECT a.*,j.title,j.recruiter_id FROM applications a JOIN jobs j ON j.id=a.job_id
                 WHERE a.id=%s""",(app_id,),one=True)
    if not row or row["recruiter_id"]!=session["user_id"]: return jsonify({"error":"Not found"}),404
    execute("UPDATE applications SET status=%s WHERE id=%s",(status,app_id))
    execute("INSERT INTO notifications(user_id,title,message) VALUES(%s,%s,%s)",
            (row["seeker_id"],"Application update",f"Your application for {row['title']} is now {status}."))
    return jsonify({"message":"Application updated"})

@app.get("/api/recommendations")
@auth_required("job_seeker")
def recommendations():
    p=query("SELECT * FROM seeker_profiles WHERE user_id=%s",(session["user_id"],),one=True) or {}
    js=query("""SELECT j.*,rp.company_name FROM jobs j JOIN recruiter_profiles rp ON rp.user_id=j.recruiter_id
                WHERE j.status='open' ORDER BY j.created_at DESC""")
    return jsonify({"recommendations":recommend_jobs(p,js)[:10]})

@app.get("/api/skills-gap/<int:job_id>")
@auth_required("job_seeker")
def gap(job_id):
    j=query("SELECT * FROM jobs WHERE id=%s",(job_id,),one=True)
    p=query("SELECT * FROM seeker_profiles WHERE user_id=%s",(session["user_id"],),one=True) or {}
    if not j:return jsonify({"error":"Job not found"}),404
    return jsonify(skills_gap(p,j))

@app.get("/api/notifications")
@auth_required()
def notifications():
    return jsonify({"notifications":query("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 30",(session["user_id"],))})

@app.patch("/api/notifications/<int:nid>/read")
@auth_required()
def read_notification(nid):
    execute("UPDATE notifications SET is_read=1 WHERE id=%s AND user_id=%s",(nid,session["user_id"]))
    return jsonify({"message":"Marked read"})

@app.get("/api/companies")
def companies():
    rows = query("""SELECT rp.company_name, rp.company_description, rp.company_location, rp.website,
                          COUNT(j.id) AS open_jobs
                   FROM recruiter_profiles rp
                   JOIN users u ON u.id=rp.user_id
                   LEFT JOIN jobs j ON j.recruiter_id=u.id AND j.status='open'
                   GROUP BY rp.id
                   ORDER BY open_jobs DESC, rp.company_name ASC""")
    return jsonify({"companies": rows})

@app.get("/api/admin/stats")
@auth_required("admin")
def admin_stats():
    return jsonify({
        "users": query("SELECT COUNT(*) c FROM users",one=True)["c"],
        "seekers": query("SELECT COUNT(*) c FROM users WHERE role='job_seeker'",one=True)["c"],
        "recruiters": query("SELECT COUNT(*) c FROM users WHERE role='recruiter'",one=True)["c"],
        "jobs": query("SELECT COUNT(*) c FROM jobs",one=True)["c"],
        "applications": query("SELECT COUNT(*) c FROM applications",one=True)["c"],
    })

@app.get("/api/admin/users")
@auth_required("admin")
def admin_users():
    return jsonify({"users":query("SELECT id,name,email,role,location,created_at FROM users ORDER BY created_at DESC")})

@app.delete("/api/admin/users/<int:user_id>")
@auth_required("admin")
def delete_user(user_id):
    if user_id==session["user_id"]: return jsonify({"error":"You cannot delete your own account"}),400
    execute("DELETE FROM users WHERE id=%s",(user_id,))
    return jsonify({"message":"User deleted"})

@app.get("/")
def index(): return send_from_directory(app.static_folder,"index.html")

@app.get("/<path:path>")
def static_files(path):
    full=os.path.join(app.static_folder,path)
    if os.path.isfile(full): return send_from_directory(app.static_folder,path)
    return send_from_directory(app.static_folder,"index.html")

if __name__=="__main__":
    try: init_demo_data()
    except Exception as e: print("Database initialization warning:",e)
    app.run(debug=True)
