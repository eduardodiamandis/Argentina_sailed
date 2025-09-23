import os
import time
import datetime
import pandas as pd
import webbrowser
import logging

logger = logging.getLogger("argentina_logger")

def process_file(url: str, file_name: str, destination_path: str,
                 sheet_name: str = None, skiprows: int = None, timeout: int = 60) -> None:
    """
    Abre uma URL no navegador, espera o download de um Excel,
    processa o arquivo e salva com data no nome.
    """

    download_path = os.path.join(os.path.expanduser('~'), 'Downloads', file_name)

    # Abrir a URL no navegador
    try:
        webbrowser.open(url)
        logger.info(f"Navegador aberto em: {url}")
    except Exception as e:
        logger.error(f"Erro ao abrir navegador: {e}")
        return

    # Esperar o download
    logger.info(f"Aguardando download de '{file_name}'...")
    start_time = time.time()
    while not os.path.exists(download_path):
        if time.time() - start_time > timeout:
            logger.error(f"Timeout: Arquivo '{file_name}' não foi encontrado em Downloads.")
            return
        time.sleep(1)

    # Ler e salvar o Excel
    try:
        df = pd.read_excel(download_path, sheet_name=sheet_name, skiprows=skiprows)

        if isinstance(df, dict):
            for sheet, data in df.items():
                output_file_name = f"{os.path.splitext(file_name)[0]}_{sheet}_{datetime.date.today()}.xlsx"
                output_path = os.path.join(destination_path, output_file_name)
                os.makedirs(destination_path, exist_ok=True)
                data.to_excel(output_path, index=False)
                logger.info(f"Planilha '{sheet}' salva em: {output_path}")

        elif isinstance(df, pd.DataFrame):
            output_file_name = f"{os.path.splitext(file_name)[0]}_{datetime.date.today()}.xlsx"
            output_path = os.path.join(destination_path, output_file_name)
            os.makedirs(destination_path, exist_ok=True)
            df.to_excel(output_path, index=False)
            logger.info(f"Arquivo salvo em: {output_path}")

        else:
            logger.error(f"Erro: O arquivo '{file_name}' não é um Excel válido.")

    except Exception as e:
        logger.error(f"Erro ao processar o arquivo '{file_name}': {e}")

    finally:
        if os.path.exists(download_path):
            os.remove(download_path)
            logger.info(f"Arquivo original '{file_name}' removido de Downloads.")
