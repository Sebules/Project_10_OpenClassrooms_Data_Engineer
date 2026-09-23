import duckdb

# Join 2 tables with a liaison table
def join_tables_with_liaison(table1:str, column1:str, table2:str, column2:str, liaison:str, column_l1:str, column_l2:str, database:str, table_fusion:str):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    conn.sql(f"""
        CREATE OR REPLACE TABLE {database}.{table_fusion} AS (
        SELECT ec.*,
            wc.*,
        FROM {database}.{table1} wc
        JOIN {database}.{liaison} lc ON wc.{column1} = lc.{column_l1}
        JOIN {database}.{table2} ec ON ec.{column2} = lc.{column_l2}
        );
        """)
    conn.close()
    return table_fusion