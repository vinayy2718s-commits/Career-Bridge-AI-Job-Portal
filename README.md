# Career Bridge - AI-Powered Smart Job Portal

A polished academic-project starter based on the supplied synopsis. It includes Job Seeker, Recruiter, Admin, AI matching, resume parsing, skills-gap analysis, application tracking, notifications, and a multi-company demo marketplace.

## Stack
- Frontend: HTML5, CSS3, JavaScript, React 18 CDN, Bootstrap 5
- Backend: Python Flask
- AI/ML: scikit-learn TF-IDF + cosine similarity, skill overlap, ranking and skills-gap logic
- Database: MySQL
- Resume parsing: PDF and DOCX
- Local setup: VS Code + XAMPP MySQL

## Important: Python 3.14
This version is prepared for modern Python packages. The requirements file uses current-compatible minimum versions instead of the old pandas pin that can trigger a source-build error on Python 3.14.

## Windows setup
1. Extract the ZIP to a simple path such as:
   `C:\Career_Bridge_AI_Smart_Job_Portal`
2. Start **MySQL** in XAMPP. Apache is not required.
3. Open `http://localhost/phpmyadmin`
4. Import `database.sql`.
5. In VS Code terminal:
```powershell
cd C:\Career_Bridge_AI_Smart_Job_Portal
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
6. Copy `.env.example` to `.env` and keep the default XAMPP MySQL settings if root has no password.
7. Start:
```powershell
python app.py
```
8. Open `http://127.0.0.1:5000`

## Demo accounts
- Admin: `admin@careerbridge.com` / `Admin@123`
- Recruiter: `recruiter@careerbridge.com` / `Recruiter@123`
- Job seeker: `seeker@careerbridge.com` / `Seeker@123`

The demo recruiter account is kept for the synopsis workflow. On first successful database startup, the app also seeds 12 demo company profiles and 12 sample roles.

## Companies
The seeded companies are fictional demo companies for academic presentation. They are not presented as real hiring relationships. Edit `db.py` if you want to replace them with your own project-approved company names.

Included demo companies:
- TechNova Solutions
- Nexora Labs
- BrightByte Systems
- CloudPeak Technologies
- DataNest Analytics
- FinEdge Digital
- CodeCraft Labs
- OrbitSoft Technologies
- GreenGrid Tech
- ApexNova Consulting
- BlueWave Digital
- VertexAI Labs

## If you already imported an older Career Bridge database
Do not delete your Fitness Setter database. They are separate databases. For a clean demo database, create/import `career_bridge` from this ZIP before first run. The app's seed function is idempotent for the demo records.

## Troubleshooting
### Database connectivity failed
- Start MySQL in XAMPP.
- Check that `career_bridge` exists in phpMyAdmin.
- Check `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=career_bridge
DB_USER=root
DB_PASSWORD=
```
- Then restart `python app.py`.

### ModuleNotFoundError
Make sure `(venv)` is visible in the terminal, then run:
```powershell
pip install -r requirements.txt
```

## Project note
The AI layer is a transparent academic implementation, not a production-trained hiring model. Scores should be treated as project/demo signals rather than real hiring decisions.
