# Windows Quick Setup

1. Install Python 3.14.x.
2. Put the project in `C:\Career_Bridge_AI_Smart_Job_Portal` (or another path outside `htdocs`).
3. Start MySQL in XAMPP.
4. Import `database.sql` in phpMyAdmin.
5. Open VS Code terminal and run:

```powershell
cd C:\Career_Bridge_AI_Smart_Job_Portal
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python app.py
```

6. Open `http://127.0.0.1:5000`.

Apache is not required because Flask serves the website. XAMPP is being used for MySQL.
