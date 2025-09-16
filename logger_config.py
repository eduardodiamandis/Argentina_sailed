import logging
import os
import datetime
import smtplib
import ssl
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# ===== Função para enviar e-mail =====
def send_error_email(log_file):
    smtp_server = "smtp.gmail.com"
    port = 587  # TLS
    sender_email = GMAIL_USER
    password = GMAIL_APP_PASSWORD

    # Lista de destinatários
    to_emails = ["eduardo.diamandis@zgbr.com.br", "Fernando.Malavolta@zgbr.com.br"]

    subject = "Erro no processo Argentina"
    body = "Ocorreu um erro durante a execução do script. Veja o log em anexo."

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_alternative(f"<h2>{body}</h2>", subtype="html")

    # Anexar arquivo de log
    if os.path.exists(log_file):
        with open(log_file, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(log_file)
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    # Conectar e enviar
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.send_message(msg)

# ===== Configurar logger =====
def setup_logger():
    log_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Argentina", "Sailed", "backup", "logs")
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"process_log_{datetime.date.today()}.log")

    logger = logging.getLogger("ArgentinaLogger")
    logger.setLevel(logging.INFO)

    # Handler de arquivo (rotativo, 5MB por arquivo, 3 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    # Handler de console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Handler para enviar e-mail apenas em ERROR
    class EmailHandler(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.ERROR:
                send_error_email(log_file)

    logger.addHandler(EmailHandler())

    return logger
