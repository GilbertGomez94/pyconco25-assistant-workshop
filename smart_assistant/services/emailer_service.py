import smtplib, ssl
from email.message import EmailMessage
from smart_assistant.deps import get_settings

def send_email(to_email: str, subject: str, body: str) -> None:
    cfg = get_settings()                 # asegúrate de que contenga la APP PASSWORD
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = cfg.email_user
    msg["To"]      = to_email
    msg.set_content(body)

    smtp_server = "smtp.gmail.com"
    smtp_port   = 587                    # STARTTLS
    context     = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context) # cifra la conexión
        server.ehlo()
        server.login(cfg.email_user, cfg.email_password)
        server.send_message(msg)
