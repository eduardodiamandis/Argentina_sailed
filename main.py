from logging import basicConfig

from sailde import process_file
import os
import  logging
import datetime
if __name__ == "__main__":
    # Configuração do logging
    log_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'logs')
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"process_log_{datetime.date.today()}.log")

    logging.basicConfig(
        level=logging.INFO,  # níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # salva em arquivo
            logging.StreamHandler()  # também mostra no console
        ]
    )

    logging.info("inicio do processo")
    # URLs
    Line_Up = 'https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mekudkcidae'
    Sailed = 'https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mlod-sfb1uu'

    # Pastas de backup
    backup_sailed = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'sailed_vessel')
    backup_line_up = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'line_vessel')

    # Dicionários com parâmetros
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
        logging.info('Processando Sailed')
        process_file(
        url=sailed['url'],
        file_name=sailed['file_name'],
        destination_path=sailed['destination_path'],
        timeout=sailed['timeout']
        )
    except Exception as error:
        logging.error(f'Error processando Sailed: {error}')

    try:
        logging.info('Processando Line_Up')

        process_file(
            url=line_up['url'],
            file_name=line_up['file_name'],
            destination_path=line_up['destination_path'],
            timeout=line_up['timeout']
        )
    except Exception as error:
        logging.error(f'Error processando Line_Up: {error}')

    logging.info('Processo finalizado')

