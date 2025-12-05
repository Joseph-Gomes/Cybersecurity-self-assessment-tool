import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

load_dotenv()

smtp_user = os.getenv("CYBER_TOOLKIT_EMAIL")
smtp_pass = os.getenv("CYBER_TOOLKIT_APP_PASSWORD")

print("Loaded email:", smtp_user)
print("Loaded password:", smtp_pass[:4] + "********")  # hide most of password

msg = MIMEMultipart()
msg["Subject"] = "Cyber Toolkit – SMTP Test"
msg["From"] = smtp_user
msg["To"] = smtp_user

msg.attach(MIMEText("If you see this email, your SMTP settings work."))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    print("Email sent!")
except Exception as e:
    print("ERROR:", e)
