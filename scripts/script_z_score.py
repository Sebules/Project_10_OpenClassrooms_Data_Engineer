import duckdb
import pandas as pd

#Script Python calcul Z-score
def z_score(table, database:str, column:str, new_column:str):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    data_products = conn.sql(f"SELECT * FROM {database}.{table}").df()
    data_products['z-score']=(
        (data_products[column]-data_products[column].mean())
        /data_products[column].std()
    )
    data_products[new_column]=0
    data_products.loc[data_products['z-score']>2, new_column]=1

    # Chargement de la database dans DuckDB
    conn.execute(f"""
                CREATE OR REPLACE TABLE {database}.{table}_z
                AS (SELECT *
                FROM data_products);
                """
                )
    conn.sql(f"FROM {database}.{table}_z LIMIT 5")

    table_z = f"{database}.{table}_z"

    conn.close()

    return table_z