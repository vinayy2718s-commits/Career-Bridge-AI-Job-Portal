# Career Bridge — online deployment checklist

This project uses Flask + MySQL. It needs a hosted MySQL database as well as a web service; deploying only the Python files will not make registration/login work.

## 1. Push code to GitHub
1. Create a GitHub repository.
2. Upload/extract this project and push the files.
3. Do not upload `.env`, passwords, API keys, `venv/`, or real resumes. `.gitignore` is included.

## 2. Create a hosted MySQL database
Create a MySQL database with a provider that gives you host, port, database name, username, and password. Keep those values private.

Import `database.sql` into that hosted database using the provider's SQL console or a MySQL client. This schema uses MySQL-specific syntax.

## 3. Deploy the web service
On a Python-compatible host (for example Render), create a Web Service from the GitHub repository.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

Add these environment variables in the host dashboard:
- `SECRET_KEY`: a long random secret value
- `DB_HOST`: hosted MySQL hostname
- `DB_PORT`: hosted MySQL port (often 3306)
- `DB_NAME`: database name
- `DB_USER`: database username
- `DB_PASSWORD`: database password
- `UPLOAD_FOLDER`: `uploads`

Do not use the local `.env.example` database settings in production. The app currently seeds demo data only when run directly with `python app.py`; before public deployment, run the project's `init_demo_data()` once using a controlled one-off command after the database schema is imported, or arrange for the seed function to be called by a safe one-off admin task. Do not expose default demo passwords for a real production service.

## 4. Verify
Open `https://YOUR-SERVICE-URL/api/health`. Expected JSON includes `"ok": true`. Then open the root URL to view the frontend. Test registration, login, job listings, and resume upload.

## Important limitations
- A host's temporary filesystem may not retain uploaded resumes after restart/redeploy. Use persistent storage or object storage if uploaded files must persist.
- Configure secure session cookies/HTTPS for production and replace the development secret.
- The database must be reachable from the web service. A public URL is not created until you complete deployment in your own hosting account.
