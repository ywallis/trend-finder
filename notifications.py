import os
import smtplib
from dotenv import load_dotenv

# Load and import credentials from ENV

load_dotenv()

SENDER = os.getenv('SENDER')

PASSWORD = os.getenv('PASSWORD')

RECIPIENT = os.getenv('RECIPIENT')

def send_email(subject, message):

    with smtplib.SMTP('smtp.gmail.com', 587) as email_out:
        email_out.starttls()
        email_out.login(SENDER, PASSWORD)
        email_out.sendmail(SENDER, [RECIPIENT], f"Subject:{subject} \n\n {message}")