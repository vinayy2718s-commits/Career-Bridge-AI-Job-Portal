# Demo Companies

Career Bridge ships with 12 fictional demo companies so the job portal looks populated during a college presentation.

Each company gets one sample role. The records are created by `db.py` when `python app.py` starts and the record does not already exist.

To add another company, add a tuple to the `companies` list in `db.py` and add a matching job tuple to the `jobs` list. Keep the same order so each company receives one role.

For a real deployment, replace demo companies with organizations you have permission to represent and use their verified company details.
