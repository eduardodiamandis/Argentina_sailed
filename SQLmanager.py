import pyodbc


def recriar_tabela_no_lugar_certo():
    # Conectamos especificando o banco para garantir o local
    conn_str = "DRIVER={SQL Server};SERVER=Server;DATABASE=ArgentinaBD;Trusted_Connection=yes;"
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    print("Limpando possíveis tabelas fantasmagóricas no master...")
    # (Opcional) Tenta apagar se você criou no master sem querer
    try:
        conn_master = pyodbc.connect("DRIVER={SQL Server};SERVER=Server;DATABASE=master;Trusted_Connection=yes;",
                                     autocommit=True)
        conn_master.cursor().execute("IF OBJECT_ID('Arg_Sailed', 'U') IS NOT NULL DROP TABLE Arg_Sailed")
        conn_master.close()
    except:
        pass

    print("Criando a tabela Arg_Sailed DENTRO do ArgentinaBD...")
    # Cria a tabela garantindo o banco correto
    cursor.execute("""
        IF OBJECT_ID('[dbo].[Arg_Sailed]', 'U') IS NOT NULL 
            DROP TABLE [dbo].[Arg_Sailed];

        CREATE TABLE [dbo].[Arg_Sailed](
            [Date] [datetime] NULL,
            [Destination] [nvarchar](255) NULL,
            [Origin] [nvarchar](255) NULL,
            [Cargo] [nvarchar](255) NULL,
            [Tons] [float] NULL,
            [Month] [int] NULL,
            [Year] [int] NULL
        );
    """)

    print("Sucesso! Tabela criada no local correto.")
    conn.close()


if __name__ == "__main__":
    recriar_tabela_no_lugar_certo()