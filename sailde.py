import os
import time
import datetime
import pandas as pd
import webbrowser


def process_file(url: str, file_name: str, destination_path: str,
                 sheet_name: str = None, skiprows: int = None, timeout: int = 60) -> None:
    """
    Abre uma URL no navegador, espera o download de um Excel,
    processa o arquivo e salva com a data no nome.

    Parâmetros:
        url (str): Link do arquivo para download.
        file_name (str): Nome esperado do arquivo baixado.
        destination_path (str): Pasta onde o arquivo processado será salvo.
        sheet_name (str, opcional): Nome da aba específica a ser lida.
        skiprows (int, opcional): Número de linhas a pular no início.
        timeout (int, opcional): Tempo máximo de espera pelo download.
    """

    download_path = os.path.join(os.path.expanduser('~'), 'Downloads', file_name)

    # Abrir a URL no navegador padrão
    try:
        webbrowser.open(url)
        print(f"Navegador aberto em: {url}")
    except Exception as e:
        print(f"Erro ao abrir navegador: {e}")
        return

    # Aguardar até o arquivo aparecer em Downloads
    print(f"Aguardando download de '{file_name}'...")
    start_time = time.time()
    while not os.path.exists(download_path):
        if time.time() - start_time > timeout:
            print(f"Timeout: Arquivo '{file_name}' não foi encontrado em Downloads.")
            return
        time.sleep(1)

    # Nome base do arquivo de saída com data
    output_file_name = f"{os.path.splitext(file_name)[0]}_{datetime.date.today()}.xlsx"
    output_path = os.path.join(destination_path, output_file_name)

    # Ler e salvar
    try:
        df = pd.read_excel(download_path, sheet_name=sheet_name, skiprows=skiprows)

        os.makedirs(destination_path, exist_ok=True)

        if isinstance(df, dict):  # múltiplas abas
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet, data in df.items():
                    data.to_excel(writer, sheet_name=sheet, index=False)
                    print(f"Planilha '{sheet}' salva em: {output_path}")
        elif isinstance(df, pd.DataFrame):  # única aba
            df.to_excel(output_path, index=False)
            print(f"Arquivo salvo em: {output_path}")
        else:
            print(f"Erro: O arquivo '{file_name}' não é um Excel válido.")

    except Exception as e:
        print(f"Erro ao processar o arquivo '{file_name}': {e}")

    finally:
        if os.path.exists(download_path):
            os.remove(download_path)
            print(f"Arquivo original '{file_name}' removido de Downloads.")
