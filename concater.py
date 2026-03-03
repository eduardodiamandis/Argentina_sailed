#!/usr/bin/env python3
"""
Atualizador do banco 'Arg_sailed_database.xlsx' — versão corrigida mantendo a lógica original de leitura.
"""
from __future__ import annotations

import pyodbc
import win32com.client as win32
import datetime
import logging
import openpyxl
from pathlib import Path
from typing import Optional

import pandas as pd
from logging.handlers import RotatingFileHandler

# mantenho a importação do seu módulo exactly como antes
try:
    from latest_module import latest_file  # type: ignore
except Exception:
    latest_file = None  # será validado mais abaixo

logger = logging.getLogger("argentina_logger")

# Caminho do banco padrão (igual ao seu original)
DATA_BASE_DEFAULT = Path.home() / "Desktop" / "Argentina" / "Arg_sailed_database.xlsx"

# Caminho OneDrive pedido por você
ONEDRIVE_DIR = Path(
    r"C:\Users\server\OneDrive - CGB Enterprises, Inc\ZGC-PBI Research - Documents 1\Dataset Data Files\Trade Flow\ARG"
)
ONEDRIVE_FILENAME = "Arg_sailed_databease.xlsx"  # conforme pedido


def setup_logger(logfile: Optional[Path] = None) -> None:
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    fh = RotatingFileHandler(logfile or (Path.home() / "argentina_updater.log"), maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)


# ---------- função original (SEM alteração) ----------
def cortar_apos_duas_vazias(df: pd.DataFrame) -> pd.DataFrame:
    """Remove linhas após duas linhas completamente vazias consecutivas."""
    empty_rows = df.isna().all(axis=1).astype(int)
    idx = None
    for i in range(len(empty_rows) - 1):
        if empty_rows.iloc[i] == 1 and empty_rows.iloc[i + 1] == 1:
            idx = i
            break
    if idx is not None:
        df = df.iloc[:idx]
    return df


def get_file_age_days(path: Path) -> Optional[int]:
    """Calcula quantos dias se passaram desde a última modificação física do arquivo."""
    if not path.exists():
        return None
    mtime = path.stat().st_mtime
    last_mod_date = datetime.date.fromtimestamp(mtime)
    today = datetime.date.today()
    return (today - last_mod_date).days


def salvar_no_sqlserver(df: pd.DataFrame):
    try:
        # 1. Conexão direta com o nome confirmado: ArgentinaBD
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=Server;"
            "DATABASE=ArgentinaBD;"
            "Trusted_Connection=yes;"
        )

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Otimização de velocidade
        cursor.fast_executemany = True

        # 2. Limpeza usando o Schema completo (dbo)
        logger.info("Limpando a tabela [dbo].[Arg_Sailed]...")
        cursor.execute("DELETE FROM [dbo].[Arg_Sailed]")

        # 3. Preparação dos dados (Garantindo tipos corretos para o MSSQL)
        # Convertemos para tipos nativos do Python para evitar erros de 'Object' do Pandas
        df_sql = df.copy()
        df_sql['Date'] = pd.to_datetime(df_sql['Date']).dt.date  # Para o tipo 'date' do SQL
        df_sql['Tons'] = pd.to_numeric(df_sql['Tons'], errors='coerce').fillna(0).astype(float)
        df_sql['Month'] = pd.to_numeric(df_sql['Month'], errors='coerce').fillna(0).astype(int)
        df_sql['Year'] = pd.to_numeric(df_sql['Year'], errors='coerce').fillna(0).astype(int)

        # Selecionamos apenas as colunas que batem com a sua tabela do SQL
        colunas = ['Date', 'Destination', 'Origin', 'Cargo', 'Tons', 'Month', 'Year']
        valores = df_sql[colunas].values.tolist()

        # 4. Inserção em massa
        query = """
                INSERT INTO [dbo].[Arg_Sailed]
                    (Date, Destination, Origin, Cargo, Tons, Month, Year)
                VALUES (?, ?, ?, ?, ?, ?, ?) \
                """

        logger.info(f"Enviando {len(valores)} linhas para o SQL Server...")
        cursor.executemany(query, valores)

        conn.commit()
        conn.close()
        logger.info("Processo SQL concluído com sucesso!")

    except Exception as e:
        logger.error(f"Falha na sincronização SQL: {e}")
        raise
def concater(df: pd.DataFrame, db: pd.DataFrame) -> pd.DataFrame:
    """Concatena df novo ao banco db, evitando duplicações mensais."""
    df["Date"] = pd.to_datetime(df["Date"])
    db["Date"] = pd.to_datetime(db["Date"])

    # Extrai mês e ano do df
    df["Month_Year"] = df["Date"].dt.to_period("M")

    months_to_remove = df["Month_Year"].unique()
    db_filtered = db[~db["Date"].dt.to_period("M").isin(months_to_remove)].copy()

    # Concatena
    db_concated = pd.concat([db_filtered, df.drop(columns=["Month_Year"])], ignore_index=True)

    # Extrai mês e ano das datas
    month_values = db_concated["Date"].dt.month
    year_values = db_concated["Date"].dt.year

    # Lógica de inserção de colunas (mantive como no seu original melhorado)
    if "Charter" in db_concated.columns:
        idx = db_concated.columns.get_loc("Charter") + 1
    else:
        idx = len(db_concated.columns)

    if "Month" not in db_concated.columns:
        db_concated.insert(idx, "Month", month_values)
    else:
        db_concated["Month"] = month_values

    if "Year" not in db_concated.columns:
        year_idx = db_concated.columns.get_loc("Month") + 1
        db_concated.insert(year_idx, "Year", year_values)
    else:
        db_concated["Year"] = year_values

    novas_linhas = len(db_concated) - len(db)
    logger.info(f"Foram adicionadas {novas_linhas} novas linhas ao banco.")

    return db_concated


def save_one_local_sheet(df: pd.DataFrame, path: Path) -> None:
    """Salva apenas a sheet 'data_base' no arquivo local (comportamento antigo)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # grava apenas uma sheet com todo o db, como você pediu
    with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, sheet_name="data_base", index=False)
    logger.info(f"Arquivo local salvo (apenas data_base): {path}")


def save_onedrive_with_extra_sheets(df: pd.DataFrame, path: Path) -> None:
    """Salva o arquivo no OneDrive com as sheets extras pedidas."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # garante Year
    if "Year" not in df.columns:
        df["Year"] = pd.to_datetime(df["Date"]).dt.year

    # detecta coluna de toneladas (tons) ou cria se não tiver
    tons_col = None
    for candidate in ("Tons", "tons", "Quantity", "Tonnes", "TONS"):
        if candidate in df.columns:
            tons_col = candidate
            break
    if tons_col is None:
        df = df.copy()
        df["Tons"] = 1
        tons_col = "Tons"
        logger.warning("Nenhuma coluna de toneladas encontrada no DataFrame; criei 'Tons' = 1 para agregação.")

    df_2025 = df[df["Year"] == 2025].copy()
    df_2026 = df[df["Year"] == 2026].copy()

    pivot_2025 = df_2025.groupby("Destination", dropna=False)[tons_col].sum().reset_index().rename(columns={tons_col: "Sum of Tons"})
    pivot_2026 = df_2026.groupby("Destination", dropna=False)[tons_col].sum().reset_index().rename(columns={tons_col: "Sum of Tons"})

    with pd.ExcelWriter(path, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, sheet_name="data_base", index=False)
        df_2025.to_excel(writer, sheet_name="2025", index=False)
        df_2026.to_excel(writer, sheet_name="2026", index=False)
        pivot_2025.to_excel(writer, sheet_name="Pivot_2025", index=False)
        pivot_2026.to_excel(writer, sheet_name="Pivot_2026", index=False)

    logger.info(f"Arquivo OneDrive salvo com sheets extras: {path}")

def criar_pivots_excel(path_excel):
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False

    wb = excel.Workbooks.Open(path_excel)

    ws_data = wb.Worksheets("data_base")

    # Range de dados
    last_row = ws_data.Cells(ws_data.Rows.Count, 1).End(-4162).Row
    last_col = ws_data.Cells(1, ws_data.Columns.Count).End(-4159).Column
    data_range = ws_data.Range(ws_data.Cells(1, 1), ws_data.Cells(last_row, last_col))

    pcache = wb.PivotCaches().Create(SourceType=1, SourceData=data_range)

    # ===== Pivot 2026 =====
    ws_p2026 = wb.Worksheets("Pivot_2026")
    ws_p2026.Cells.Clear()

    pt2026 = pcache.CreatePivotTable(ws_p2026.Range("A3"), "Pivot_2026")

    pt2026.PivotFields("Destination").Orientation = 1  # Rows
    pt2026.AddDataField(pt2026.PivotFields("Tons"), "Sum of Tons", -4157)

    # Filters
    pt2026.PivotFields("Year").Orientation = 3
    pt2026.PivotFields("Origin").Orientation = 3
    pt2026.PivotFields("Cargo").Orientation = 3
    pt2026.PivotFields("Month").Orientation = 3

    pt2026.PivotFields("Year").CurrentPage = "2026"
    pt2026.PivotFields("Origin").CurrentPage = "ARGENTINA"
    pt2026.PivotFields("Cargo").CurrentPage = "CORN"

    mes_atual = str(datetime.datetime.now().month)
    pt2026.PivotFields("Month").CurrentPage = mes_atual

    # ===== Pivot 2025 =====
    ws_p2025 = wb.Worksheets("Pivot_2025")
    ws_p2025.Cells.Clear()

    pt2025 = pcache.CreatePivotTable(ws_p2025.Range("A3"), "Pivot_2025")

    pt2025.PivotFields("Destination").Orientation = 1
    pt2025.AddDataField(pt2025.PivotFields("Tons"), "Sum of Tons", -4157)

    pt2025.PivotFields("Year").Orientation = 3
    pt2025.PivotFields("Origin").Orientation = 3
    pt2025.PivotFields("Cargo").Orientation = 3
    pt2025.PivotFields("Month").Orientation = 3

    pt2025.PivotFields("Year").CurrentPage = "2025"
    pt2025.PivotFields("Origin").CurrentPage = "ARGENTINA"
    pt2025.PivotFields("Cargo").CurrentPage = "CORN"
    pt2025.PivotFields("Month").CurrentPage = "12"

    wb.Save()
    wb.Close()
    excel.Quit()

def jun():
    setup_logger()
    logger.info("Iniciando rotina de atualização de banco Arg_sailed_database.xlsx")

    try:
        # Verifica se latest_file foi importado corretamente (mesmo comportamento do seu original)
        if latest_file is None:
            logger.error("Variável 'latest_file' não encontrada. Certifique-se que latest_module.latest_file está disponível.")
            raise SystemExit(2)

        # Verifica idade do arquivo antes de abrir
        dias_desde_att = get_file_age_days(DATA_BASE_DEFAULT)
        if dias_desde_att is not None:
            logger.info(f"O arquivo de banco de dados foi modificado pela última vez há {dias_desde_att} dias.")
        else:
            logger.warning("Arquivo de banco de dados não encontrado para verificar data de modificação.")

        logger.info(f"Lendo banco base: {DATA_BASE_DEFAULT}")
        db = pd.read_excel(DATA_BASE_DEFAULT)

        logger.info(f"Lendo arquivo mais recente: {latest_file} (header=7, conforme original)")
        # manteve exatamente header=7 — sem tentativa automática de detectar header
        df = pd.read_excel(latest_file, header=7,engine="openpyxl")

        # mantém sua função original de cortar após duas linhas vazias — SEM alteração
        df = cortar_apos_duas_vazias(df)

        # concatena com sua lógica
        atualizado = concater(df, db)

        #parte em sql
        salvar_no_sqlserver(atualizado)

        # salva local (apenas data_base) — comportamento original preservado
        output_local = DATA_BASE_DEFAULT.parent / "Arg_sailed_database_AT.xlsx"
        save_one_local_sheet(atualizado, output_local)

        # salva no OneDrive com sheets extras solicitadas
        one_drive_file = ONEDRIVE_DIR / ONEDRIVE_FILENAME
        save_onedrive_with_extra_sheets(atualizado, one_drive_file)

        # Correção do Log: Usando tail() e to_string() para garantir visibilidade
        # Garante datetime
        atualizado["Date"] = pd.to_datetime(atualizado["Date"])

        # Ordena do mais recente para o mais antigo
        ultimas_15 = (
            atualizado
            .sort_values(by="Date", ascending=False)
            .head(15)
            .sort_values(by="Date")  # reordena essas 15 do mais antigo → mais novo
        )

        ultimas_datas = ultimas_15["Date"].dt.strftime('%d/%m/%Y').to_string(index=False)

        logger.info(f"Últimas 15 datas no banco atualizado:\n{ultimas_datas}")
        one_drive_file = ONEDRIVE_DIR / ONEDRIVE_FILENAME
        save_onedrive_with_extra_sheets(atualizado, one_drive_file)

        criar_pivots_excel(str(one_drive_file))

    except Exception as e:
        logger.exception(f"Erro durante o processo de concatenação: {e}")


if __name__ == "__main__":
    jun()