# Création des tables dans la database
import duckdb
from pathlib import Path

def creation_table(url,database:str):
    """
    Creation de tables dans la database DuckDB à partir d'un chemin d'accès en local. 
    Les fichiers sont des .xlsx. La fonction ne fonctionne que pour des fichiers Excel.
    """
    conn =  duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    tables_export = []
    for file in url:
        nom_table = Path(file).stem.split('_')[-1] + "_export_data"
        conn.sql(f"CREATE OR REPLACE TABLE {database}.{nom_table} AS SELECT * FROM read_xlsx('{file}',all_varchar=true );")
        print(f"table {nom_table} créée dans la database DuckDB {database}.db")
        print(conn.sql(f"FROM {database}.{nom_table} LIMIT 5"))
        tables_export.append(nom_table)

    conn.close()


    return tables_export