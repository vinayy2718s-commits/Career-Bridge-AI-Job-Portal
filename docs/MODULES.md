# Module mapping from synopsis

## Admin
User management, platform statistics and job monitoring endpoints are under `/api/admin/*`.

## Job Seeker
Registration, profile, resume upload, job search, apply, application tracking, AI recommendations and skills-gap analysis.

## Recruiter
Company profile, job posting, candidate list and AI ranking, application status updates.

## AI/ML
`ai_engine.py` implements:
1. Resume/profile text processing
2. TF-IDF + cosine similarity
3. Required-skill overlap
4. Candidate ranking
5. Skills-gap extraction and learning recommendations

## Notification
`notifications` table plus API endpoints. Notifications are generated when an application is submitted or status changes.

## Limitations reflected from synopsis
No real-time chat, external job-board integration or video interview integration is implemented in this version. Resume parsing currently focuses on PDF/DOCX.
