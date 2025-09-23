import pandas as pd
import os


directory =os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Sailed', 'backup', 'sailed_vessel')

def get_latest_file(directory:str)-> str | None:
    """

    Parameters
    ----------

    directory: path where the files are located

    Returns path of the latest file
    -------

    """
    try:
        files = [os.path.join(directory, f) for f in os.listdir(directory)
                 if os.path.isfile(os.path.join(directory, f))]
        if not files:
            return None
        latest_file = max(files, key=os.path.getctime)
        return latest_file
    except Exception as e:
        print(f"Erro ao buscar arquivos: {e}")
        return None

latest_file = get_latest_file(directory)




# demonstration
if __name__ == "__main__":

    print(f"Latest file: {latest_file}")
