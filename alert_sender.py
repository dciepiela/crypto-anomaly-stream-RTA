import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

def load_subscribers(path="subscribers.txt"):
    """Ładuje listę subskrybentów z pliku"""
    try:
        with open(path, "r") as f:
            subscribers = [line.strip() for line in f if line.strip()]
            return subscribers
    except Exception as e:
        return []

def send_email_alert(subject, body, recipients):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        print(f"📧 Wysłano do: {recipients}")
    except Exception as e:
        print(f"❌ Email error: {e}")
