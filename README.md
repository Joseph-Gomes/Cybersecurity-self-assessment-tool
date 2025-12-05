## 🛡️ Cybersecurity Self-Assessment Toolkit

This interactive toolkit helps small and medium businesses quickly evaluate their cybersecurity posture.
It guides users through a set of assessment questions, calculates their security score, visualizes results with professional charts, and generates a downloadable PDF report with recommendations.

Built using Python, Streamlit, Matplotlib, and FPDF, the toolkit runs locally and requires no backend.

## Features
✔ Interactive Cybersecurity Assessment

Users answer 20 yes/no questions across five key cybersecurity areas:

Identify
Protect
Detect & Respond
Recover
Governance & People

✔ Automated Scoring

The system calculates:
Overall security score
Internal risk points
Risk percentage
Risk level (LOW / MEDIUM / HIGH)
Pillar-by-pillar score breakdown

✔ Smart Recommendations
Each unsafe answer produces tailored, easy-to-understand recommendations for improving security.

✔ Professional Visual Charts
Generated with Matplotlib:
Radar (spider) chart showing multi-pillar performance
Bar chart illustrating individual pillar scores
Charts appear both on the webpage and inside the PDF report.

✔ PDF Report Generation
The downloadable PDF includes:
Participant details
Summary results
Visual charts
Recommendations
Exported as a clean, professional report suitable for sharing with team members, clients, or IT providers.

✔ Email Delivery (Optional)
Users can send themselves a copy of the PDF report.
Email uses Gmail SMTP via .env configuration.

✔ Restart Assessment Feature
Allows users to clear previous results and start again.

## Technology Stack
Component	             Technology
Web App UI	             Streamlit
Charts	                 Matplotlib + NumPy
PDF Generation	         FPDF
Email Sending	         smtplib
Config Management	     python-dotenv
Questionnaire	         JSON

## 📂 Project Structure
cybersecurity-toolkit/
│
├── app/
│   ├── web_app.py         # Main Streamlit application
│   ├── logic.py           # Scoring + recommendations engine
│   ├── pdf_generator.py   # Placeholder for optional future PDF logic
│   └── __init__.py
│
├── data/
│   └── questions.json     # Assessment questions + metadata
│
├── .env                   # Email settings (ignored by Git)
├── requirements.txt       # Dependencies
└── README.md

## 🛠️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/Joseph-Gomes/Cybersecurity-self-assessment-tool.git
cd Cybersecurity-self-assessment-tool

2️⃣ Create a virtual environment
python -m venv .venv

3️⃣ Activate the environment
Windows:
.venv\Scripts\activate
Mac/Linux:
source .venv/bin/activate

4️⃣ Install dependencies
pip install -r requirements.txt

📧 Email Configuration (Optional)

To enable “Send report to my email”, create a .env file in the project root:

CYBER_TOOLKIT_EMAIL=yourgmail@gmail.com
CYBER_TOOLKIT_APP_PASSWORD=your_app_password

## Important:
You must use a Google App Password, not your regular Gmail password.
This requires:
Enabling 2-Step Verification
Generating an App Password
Instructions: https://support.google.com/accounts/answer/185833
If .env is missing or incomplete, the app will still run — email sending will simply be disabled.

▶️ Running the Toolkit
Once dependencies are installed, run:
streamlit run app/web_app.py
Then open the URL shown in your terminal

## PDF Output Example
The generated PDF includes:
User-entered details
Security score summary
Radar (spider) chart
Bar chart
Action recommendations
The PDF is suitable for printing, sharing, or archiving.

## Contributing
Contributions, issues, and feature ideas are welcome.
Feel free to open a GitHub Issue or submit a Pull Request.

## Security Notes
No user data is stored — responses live only in Streamlit session state.
PDF generation happens locally.
Email credentials must be stored in .env and are not committed to GitHub.
This toolkit is intended for general guidance, not formal compliance certification.

## License
This project is licensed under the MIT License, allowing commercial and personal use.

## Acknowledgements
Thanks for using this cybersecurity assessment toolkit.
It was built to help small and medium businesses better understand and strengthen their cybersecurity maturity with a simple, accessible workflow.
