import pandas as pd
import os
import datetime
from latest_module import latest_file
# Carrega os arquivos
df = pd.read_excel(latest_file, header=7)
# Remove linhas onde não conseguiu converter
def cortar_apos_duas_vazias(df):
    # Procura linhas que são totalmente vazias
    empty_rows = df.isna().all(axis=1).astype(int)

    # Procura onde aparecem duas vazias consecutivas
    idx = None
    for i in range(len(empty_rows) - 1):
        if empty_rows.iloc[i] == 1 and empty_rows.iloc[i+1] == 1:
            idx = i
            break

    # Se achou, corta até a linha antes
    if idx is not None:
        df = df.iloc[:idx]
    return df
df = cortar_apos_duas_vazias(df)

data_base = os.path.join(os.path.expanduser('~'), 'Desktop', 'Argentina', 'Arg_sailed_database.xlsx')
db = pd.read_excel(data_base)


def days_passed(df, column_name="Date"):
    """
    Calculate the number of days that have passed since the most recent date
    in the specified column of the given DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame that contains a column with datetime-like objects.
    column_name : str, optional
        The name of the column to use (default is 'Date').

    Returns
    -------
    int
        Number of days between the last date in the column and today.

    Raises
    ------
    ValueError
        If the last entry in the column is not a valid date.
    """
    today = datetime.date.today()
    last_day = df[column_name].iloc[-1]

    # Converte para date se for Timestamp ou datetime
    if isinstance(last_day, (pd.Timestamp, datetime.datetime)):
        last_day = last_day.date()

    if isinstance(last_day, datetime.date):
        return (today - last_day).days
    else:
        raise ValueError(f"Last entry in column {column_name} is not a valid date: {last_day}")


def concater(df, db):
    df["Date"] = pd.to_datetime(df["Date"])
    db["Date"] = pd.to_datetime(db["Date"])

    # Extrai mês e ano da coluna 'Date'
    df["Month_Year"] = df["Date"].dt.to_period("M")

    # Obtém os meses/anos únicos do df
    months_to_remove = df["Month_Year"].unique()

    # Remove do db linhas com meses/anos já presentes no df
    db_filtered = db[~db["Date"].dt.to_period("M").isin(months_to_remove)].copy()

    # Concatena o db filtrado com o novo df
    db_concated = pd.concat([db_filtered, df.drop(columns=["Month_Year"])], ignore_index=True)
    return db_concated


if __name__ == "__main__":
    last_update = days_passed(db)


    if last_update >= 11:
        print(latest_file)
        print("Last updated date is", last_update)
        print("Hora de atualizar")
        atualizado = concater(df, db)
        print(atualizado["Date"].tail())
        atualizado.to_execel()
    else:
        print(f"O banco já foi atualizado {last_update} dias atrás, não precisa atualizar.")
