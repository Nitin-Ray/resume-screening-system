 Smart Resume Screening & Skill Matching System (with Admin Panel)

An automated Resume Screening and Job Description (JD) Matching Web Application built with Python (Flask) and SQLite. This system helps candidates evaluate their resumes against specific job descriptions, calculates a real-time compatibility score, highlights matched and missing skills, and provides actionable improvement suggestions. It also includes a dedicated Admin Dashboard to monitor registered users and review all candidate submissions.

 Key Features

 Candidate / User Module

User Authentication: Secure Registration and Login system for candidates.

Resume Upload & Parsing: Supports uploading resumes (PDF/DOCX) and automatically extracts raw text.

Skill Extraction & JD Matching: Compares resume skills against the target Job Description using a curated skills dictionary.

Match Percentage Score: Calculates an accurate compatibility score based on required vs. possessed skills.

Smart Improvement Suggestions: Provides personalized tips and recommendations to improve the resume based on missing skills and overall score.

Submission History: Candidates can view their past resume evaluations, scores, and feedback anytime.

 Admin Module

Admin Dashboard: Centralized view of system activity, total users, and total resume evaluations.

User Management: View and inspect registered candidate profiles (admin_user.html).

Result Monitoring: Access detailed evaluation reports, match scores, and skill gaps for all candidate submissions (admin_result.html).

 Tech Stack

Backend: Python 3, Flask

Frontend: HTML5, CSS3 (style.css), Jinja2 Templates

Database: SQLite3 (database.py)

Text Processing & Matching: Custom Python modules for text extraction, skill matching, and suggestion generation

 Project Directory Structure

resume_project_with_admin/
│
├── app.py                      # Main Flask application & route controller
├── database.py                 # SQLite database connection, tables & queries
├── extractor.py                # Resume text extraction logic (PDF/DOCX)
├── matcher.py                  # Skill matching & match score calculation engine
├── skills.py                   # Master dictionary/list of technical & soft skills
├── suggestions.py              # Engine to generate resume improvement tips
├── requirements.txt            # Required Python dependencies
│
├── static/
│   └── style.css               # Custom stylesheet for UI and dashboard
│
├── templates/
│   ├── base.html               # Base template layout (Navbar & Footer)
│   ├── index.html              # Candidate main page (Upload Resume & JD)
│   ├── login.html              # User & Admin login page
│   ├── register.html           # New user registration page
│   ├── result.html             # Resume analysis result page
│   ├── _result_body.html       # Reusable partial template for result details
│   ├── history.html            # Candidate's past submissions history
│   ├── admin_dashboard.html    # Main Admin control panel
│   ├── admin_user.html         # Admin view for user details
│   └── admin_result.html       # Admin view for detailed candidate results
│
└── uploads/
    └── .gitkeep                # Directory to store uploaded resume files


⚙️ Installation & Setup Guide

Follow these steps to run the project locally on your machine:

1. Clone the Repository

git clone https://github.com/your-username/resume-project-with-admin.git
cd resume-project-with-admin


2. Create a Virtual Environment (Optional but Recommended)

# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

Install all required packages listed in requirements.txt:

pip install -r requirements.txt


4. Run the Application

python app.py


5. Open in Browser

Once the Flask server starts, open your web browser and go to:

http://127.0.0.1:5000/


 How It Works (Workflow)

Login / Register: Create a new candidate account or log in with existing credentials.

Upload & Input: Upload your resume file and paste the target Job Description (JD) on the home screen.

Analysis:

extractor.py extracts and cleans the text from the uploaded document.

matcher.py and skills.py identify technical/domain skills in both the resume and JD, computing a match percentage.

suggestions.py generates targeted tips for the missing skills.

View Results: Check your match score, matched skills, missing skills, and improvement tips on the results page, or review them later in the History tab.

Admin Review: Admins can log in to access the Admin Dashboard to oversee all registered candidates and their screening reports.

 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork this repository and submit a pull request.

License

This project is created for educational and academic purposes.