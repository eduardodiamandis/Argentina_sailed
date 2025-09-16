import logging
import os
import datetime

def setup_logger(name: str = "argentina_logger") -> logging.Logger:
    """
    Configura e retorna um logger com saída em arquivo + console.
    """
    log_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'logs')
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"process_log_{datetime.date.today()}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita duplicar handlers se chamar mais de uma vez
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
