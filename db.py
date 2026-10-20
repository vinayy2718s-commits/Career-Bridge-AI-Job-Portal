import os
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv()

def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "career_bridge"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "")
    )

def query(sql, params=(), one=False):
    cn = connect(); cur = cn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchone() if one else cur.fetchall()
    finally:
        cur.close(); cn.close()

def execute(sql, params=()):
    cn = connect(); cur = cn.cursor()
    try:
        cur.execute(sql, params); cn.commit(); return cur.lastrowid
    finally:
        cur.close(); cn.close()

def init_demo_data():
    # Admin + demo seeker/recruiter
    if not query("SELECT id FROM users WHERE email=%s", ("admin@careerbridge.com",), one=True):
        execute("INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,%s)",
                ("Career Bridge Admin", "admin@careerbridge.com", generate_password_hash("Admin@123"), "admin"))
    if not query("SELECT id FROM users WHERE email=%s", ("seeker@careerbridge.com",), one=True):
        sid = execute("INSERT INTO users(name,email,password_hash,role,location) VALUES(%s,%s,%s,%s,%s)",
                      ("Demo Job Seeker", "seeker@careerbridge.com", generate_password_hash("Seeker@123"), "job_seeker", "Mumbai"))
        execute("INSERT INTO seeker_profiles(user_id,headline,skills,experience_years,education,preferences) VALUES(%s,%s,%s,%s,%s,%s)",
                (sid, "B.Sc. IT Student", "Python, HTML, CSS, JavaScript, SQL, MySQL, React", 1, "B.Sc. IT", "Mumbai, Pune; software development"))

    companies = [
        ("TechNova Solutions", "Software, cloud and AI product engineering company.", "Mumbai", "https://example.com/technova"),
        ("Nexora Labs", "Digital products and full-stack engineering studio.", "Pune", "https://example.com/nexora"),
        ("BrightByte Systems", "Enterprise software and data engineering team.", "Bengaluru", "https://example.com/brightbyte"),
        ("CloudPeak Technologies", "Cloud, DevOps and platform engineering solutions.", "Hyderabad", "https://example.com/cloudpeak"),
        ("DataNest Analytics", "Analytics, machine learning and business intelligence.", "Mumbai", "https://example.com/datanest"),
        ("FinEdge Digital", "Fintech software and secure digital platforms.", "Mumbai", "https://example.com/finedge"),
        ("CodeCraft Labs", "Web and mobile product development studio.", "Delhi", "https://example.com/codecraft"),
        ("OrbitSoft Technologies", "Scalable web applications and API engineering.", "Chennai", "https://example.com/orbitsoft"),
        ("GreenGrid Tech", "Technology solutions for smart infrastructure.", "Ahmedabad", "https://example.com/greengrid"),
        ("ApexNova Consulting", "Technology consulting and digital transformation.", "Bengaluru", "https://example.com/apexnova"),
        ("BlueWave Digital", "Customer experience, frontend and digital platforms.", "Pune", "https://example.com/bluewave"),
        ("VertexAI Labs", "Applied AI, NLP and intelligent automation.", "Hyderabad", "https://example.com/vertexai"),
    ]
    jobs = [
        ("Junior Python Developer", "Build APIs and web applications with a collaborative engineering team.", "Python, Flask, SQL, MySQL, Git, JavaScript", 0, "Mumbai", "Software Development", 350000, 650000, "Full-time"),
        ("Frontend React Developer", "Create responsive interfaces and reusable React components.", "React, JavaScript, HTML, CSS, Git", 1, "Pune", "Frontend Development", 400000, 800000, "Full-time"),
        ("Data Analyst", "Turn business data into dashboards, insights and clear reports.", "Python, Pandas, SQL, Excel, Power BI", 0, "Mumbai", "Data Analytics", 350000, 700000, "Full-time"),
        ("Machine Learning Intern", "Support experiments, data preparation and model evaluation.", "Python, Pandas, NumPy, Scikit-learn, SQL", 0, "Hyderabad", "AI / ML", 180000, 300000, "Internship"),
        ("Java Backend Developer", "Develop reliable REST APIs and backend services.", "Java, Spring Boot, SQL, Git, REST API", 1, "Bengaluru", "Backend Development", 500000, 950000, "Full-time"),
        ("Cloud / DevOps Engineer", "Automate deployments and improve cloud infrastructure.", "AWS, Docker, Linux, Git, CI/CD", 2, "Hyderabad", "Cloud & DevOps", 650000, 1200000, "Full-time"),
        ("UI/UX Designer", "Design clear, accessible experiences for digital products.", "Figma, UI Design, UX Research, Prototyping", 1, "Pune", "Design", 350000, 750000, "Full-time"),
        ("NLP Intern", "Work on text processing and language-model experiments.", "Python, NLP, spaCy, NLTK, Machine Learning", 0, "Hyderabad", "AI / ML", 180000, 320000, "Internship"),
        ("Full Stack Developer", "Build modern web applications across frontend and backend.", "JavaScript, React, Python, Flask, MySQL", 1, "Delhi", "Full Stack", 450000, 900000, "Full-time"),
        ("SQL Developer", "Create optimized queries, reports and database workflows.", "SQL, MySQL, Database Design, Python", 1, "Chennai", "Database", 400000, 800000, "Full-time"),
        ("Business Analyst", "Translate business requirements into actionable product work.", "SQL, Excel, Power BI, Communication", 1, "Mumbai", "Business Analysis", 400000, 850000, "Full-time"),
        ("AI Automation Intern", "Prototype intelligent workflow automation features.", "Python, APIs, NLP, Machine Learning", 0, "Bengaluru", "AI / ML", 200000, 350000, "Internship"),
    ]
    for idx, (company, desc, loc, website) in enumerate(companies):
        email = "demo+" + str(idx + 1) + "@careerbridge.local"
        u = query("SELECT id FROM users WHERE email=%s", (email,), one=True)
        if not u:
            uid = execute("INSERT INTO users(name,email,password_hash,role,location) VALUES(%s,%s,%s,%s,%s)",
                          (company + " Recruiter", email, generate_password_hash("Recruiter@123"), "recruiter", loc))
            execute("INSERT INTO recruiter_profiles(user_id,company_name,company_description,website,company_location) VALUES(%s,%s,%s,%s,%s)",
                    (uid, company, desc, website, loc))
        else:
            uid = u["id"]
        # Add one job per company; safe to rerun.
        j = jobs[idx]
        exists = query("SELECT id FROM jobs WHERE recruiter_id=%s AND title=%s", (uid, j[0]), one=True)
        if not exists:
            execute("""INSERT INTO jobs(recruiter_id,title,description,required_skills,experience_required,location,category,salary_min,salary_max,job_type)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (uid, j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[7], j[8]))
