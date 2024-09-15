import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

from env import password

def send_test_email(receiver_email: str):
    sender_email = "yu.cao20041208@gmail.com"
    subject = "Test Email"

    body = f"""
    This is a test email.
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    smtp_server = "smtp.gmail.com"
    port = 587  # For TLS

    server = smtplib.SMTP(smtp_server, port)
    try:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()

def send_password_reset_email(receiver_email: str, uid: str):
    sender_email = "yu.cao20041208@gmail.com"
    subject = "Password Reset Request"

    reset_token = str(uuid.uuid4())

    reset_url = f"https://campus-connect-helper.web.app/reset.html?token={reset_token}&uid={uid}"

    body = f"""
    Hello,


    {reset_url}

    If you did not request a password reset, please ignore this email.

    Thank you,
    CampusConnect Team
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    smtp_server = "smtp.gmail.com"
    port = 587  # For TLS
    server = smtplib.SMTP(smtp_server, port)
    try:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Password reset email sent successfully!")
        return reset_token
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()