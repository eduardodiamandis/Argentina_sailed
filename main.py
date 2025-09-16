from sailde import process_file
from logger_config import setup_logger
import os

if __name__ == "__main__":
    logger = setup_logger()

    logger.info("Início do processo")

    # URLs
    Line_Up = 'https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mekudkcidae'
    Sailed = 'https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mlod-sfb1uu'

    # Pastas de backup
    backup_sailed = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'sailed_vessel')
    backup_line_up = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'line_vessel')

    sailed = {
        'url': Sailed,
        'file_name': 'vessels_sailed_update.xlsx',
        'destination_path': backup_sailed,
        'timeout': 40
    }

    line_up = {
        'url': Line_Up,
        'file_name': 'vessel_update.xlsx',
        'destination_path': backup_line_up,
        'timeout': 40
    }

    try:
        logger.info("Processando Sailed")
        process_file(**sailed)
    except Exception as error:
        logger.error(f"Erro processando Sailed: {error}")

    try:
        logger.info("Processando Line_Up")
        process_file(**line_up)
    except Exception as error:
        logger.error(f"Erro processando Line_Up: {error}")

    logger.info("Processo finalizado")
