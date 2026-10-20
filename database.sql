CREATE DATABASE IF NOT EXISTS career_bridge;
USE career_bridge;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('job_seeker','recruiter','admin') NOT NULL DEFAULT 'job_seeker',
    phone VARCHAR(30),
    location VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seeker_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    headline VARCHAR(180),
    skills TEXT,
    experience_years DECIMAL(4,1) DEFAULT 0,
    education VARCHAR(255),
    resume_filename VARCHAR(255),
    resume_text LONGTEXT,
    preferences TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recruiter_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(180) NOT NULL,
    company_description TEXT,
    website VARCHAR(255),
    company_location VARCHAR(120),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    experience_required DECIMAL(4,1) DEFAULT 0,
    location VARCHAR(120),
    category VARCHAR(100),
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    job_type VARCHAR(60) DEFAULT 'Full-time',
    status ENUM('open','closed') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    seeker_id INT NOT NULL,
    cover_note TEXT,
    status ENUM('Applied','Shortlisted','Rejected','Selected') DEFAULT 'Applied',
    match_score DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_application(job_id,seeker_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (seeker_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT IGNORE INTO skills(name) VALUES
('Python'),('Java'),('JavaScript'),('React'),('HTML'),('CSS'),('SQL'),
('MySQL'),('Flask'),('Django'),('Spring Boot'),('Machine Learning'),
('Scikit-learn'),('Pandas'),('NumPy'),('NLP'),('Git'),('AWS'),('Docker');

-- Demo users. Password hashes are generated in app.py on first run if these IDs are absent.
-- The application automatically seeds the demo accounts.
