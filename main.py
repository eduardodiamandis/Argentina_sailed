from sailde import process_file
from logger_config import setup_logger
import time

logger = setup_logger()

import concater  # agora ele herda o logger corretamente

if __name__ == "__main__":
    logger.info("Início do processo")

    try:
        logger.info("Processando Sailed...")
        process_file(
            url="https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mlod-sfb1uu",
            file_name="vessels_sailed_update.xlsx",
            destination_path=r"C:\Users\server\Desktop\Argentina\Sailed\backup\sailed_vessel",
            timeout=40
        )

        time.sleep(3)


    except Exception as e:
        logger.error(f"Erro processando Sailed: {e}")

    try:
        logger.info("Processando Line_Up...")
        process_file(
            url="https://boletines.nabsa.com.ar/c/gr6gdj/lmt8mdy1/mekudkcidae",
            file_name="vessel_update.xlsx",
            destination_path=r"C:\Users\server\Desktop\Argentina\Sailed\backup\line_vessel",
            timeout=18
        )
    except Exception as e:
        logger.error(f"Erro processando Line_Up: {e}")

    logger.info("Processo finalizado")
    try:
        logger.info("Iniciando o concatenação..")
        concater.jun()
        logger.info("Feito")
    except Exception as e:
        logger.error(f"Erro no concater: {e}")
