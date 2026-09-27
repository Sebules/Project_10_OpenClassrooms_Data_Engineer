import duckdb
from pathlib import Path
import pandas as pd

# Suppression des colonnes entièrement nulles
def delete_columns_null(tables, database):
    conn = duckdb.connect()
    columns_to_delete = {}
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    # view the columns to be delete
    for table in tables:
        conn.sql(f"CREATE OR REPLACE VIEW {database}.{table}_summarized_view AS (SUMMARIZE {database}.{table});")
        print(f"vue {database}.{table} créée")
        print(conn.sql(f"SELECT * FROM {database}.{table}_summarized_view;"))

        null_columns=conn.sql(f"SELECT column_name FROM {database}.{table}_summarized_view WHERE null_percentage = 100.0;")

        cols_to_remove = set()
        if null_columns:
            print(f"null columns from table {table} are\n{null_columns}")
            list_null_columns = [row[0] for row in null_columns.fetchall()]
            cols_to_remove.update(list_null_columns)
        else:
            print(f"no null columns in table {table}")

        zeros_columns = conn.sql(f"SELECT column_name FROM {database}.{table}_summarized_view WHERE (min = '0.0' AND max = '0.0') OR (min = '0' AND max = '0') ;")
        
        if zeros_columns:
            print(f"zeros columns from table {table} are\n{zeros_columns}")
            list_zeros_columns = [row[0] for row in zeros_columns.fetchall()]
            cols_to_remove.update(list_zeros_columns)
        else:
            print(f"no zeros columns in table {table}")

        if cols_to_remove:
                columns_to_delete[table] = cols_to_remove

    
    # create cleaned tables
    for table,columns in columns_to_delete.items():
        tables_cleaned_names = []
        columns_str = ", ".join(columns)
        conn.sql(f"CREATE OR REPLACE TABLE {database}.{table}_clean AS SELECT * EXCLUDE({columns_str}) FROM {database}.{table};")
        tables_cleaned_names.append(f"{table}_clean")

    print("COLUMNS BEFORE DELETING \n")
    print(conn.sql(f"DESCRIBE {database}.{table}"))
    print("COLUMNS AFTER DELETING \n")
    print(conn.sql(f"DESCRIBE {database}.{table}_clean"))

    conn.close()
        
    return columns_to_delete, tables_cleaned_names


# Suppression lignes entièrement nulles

def delete_null_row(tables,tables_clean,database):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    for table in tables:
        # Create table_clean if not exists.
        if f"{table}_clean" not in tables_clean:
            conn.sql(f"""CREATE OR REPLACE TABLE {database}.{table}_clean
                 AS SELECT * FROM {database}.{table};
                 """)
            tables_clean.append(f"{table}_clean")
            print(f"table {table}_clean créée")

        
        nb_rows_before =conn.sql(f"SELECT COUNT(*) FROM {database}.{table}_clean;").fetchone()[0]
        conn.sql(f"""
                    CREATE OR REPLACE TABLE {database}.{table}_clean 
                    AS FROM {database}.{table}_clean 
                    EXCEPT FROM {database}.{table}_clean 
                    WHERE COLUMNS(*) IS NULL;
                    """)
        
        nb_rows_after = conn.sql(f"SELECT COUNT(*) FROM {database}.{table}_clean;").fetchone()[0]

        print( nb_rows_before ,f"rows before in table {table}_clean" )
        print( nb_rows_after ,f"rows after in table {table}_clean" )
        print(nb_rows_before-nb_rows_after, f"null row(s) deleted in table {table}_clean")

    conn.close()                       

    return tables_clean


# Dédoublement
def dedoublement(tables, tables_clean, database):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    for table in tables:
        # Create table_clean if not exists.
        if f"{table}_clean" not in tables_clean:
            conn.sql(f"""CREATE OR REPLACE TABLE {database}.{table}_clean
                    AS SELECT * FROM {database}.{table};
                    """)
            tables_clean.append(f"{table}_clean")
            print(f"table {table}_clean créée")

        nb_rows_before =conn.sql(f"""
                                 SELECT COUNT(*) 
                                 FROM {database}.{table}_clean;
                                 """).fetchone()[0]
        conn.sql(f""" 
            CREATE OR REPLACE TABLE {database}.{table}_clean 
            AS (SELECT DISTINCT * FROM {database}.{table}_clean)
            """)
        nb_rows_after =conn.sql(f"""
                                 SELECT COUNT(*) 
                                 FROM {database}.{table}_clean;
                                 """).fetchone()[0]
        print( nb_rows_before ,f"rows before in table {table}_clean" )
        print( nb_rows_after ,f"rows after in table {table}_clean" )
        print(nb_rows_before-nb_rows_after, f"row(s) deleted in table {table}_clean")

    conn.close()  
    return tables_clean


# Conversion de format
def convert_format(tables, tables_clean, database):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    list_conv_date = ['date', 'post_modified']
    list_conv_num = ['price', 'quantity', 'total']

    for table in tables:
        describe = conn.sql(f"SELECT column_name FROM (DESCRIBE {database}.{table});")
        describe_columns = [row[0] for row in describe.fetchall()]

        # Create table_clean if not exists.
        if f"{table}_clean" not in tables_clean:
            conn.sql(f"""CREATE OR REPLACE TABLE {database}.{table}_clean
                 AS SELECT * FROM {database}.{table};
                 """)
            tables_clean.append(f"{table}_clean")
            print(f"table {table}_clean créée")
            

        for col in describe_columns:
            col_lower = col.lower()

            # DATE conversion
            if any(word in col_lower for word in list_conv_date):
                conn.sql(f"""
                    ALTER TABLE {database}.{table}_clean 
                    ALTER COLUMN {col} TYPE DATE 
                    USING (DATE '1899-12-30' + CAST(TRY_CAST({col} AS DOUBLE) AS INTEGER) * INTERVAL 1 DAY);
                """)
                print(f"colonne {col} de {table}_clean convertie en DATE")

            # DOUBLE conversion
            elif any(word in col_lower for word in list_conv_num):
                conn.sql(f"""
                    ALTER TABLE {database}.{table}_clean 
                    ALTER COLUMN {col} TYPE DOUBLE 
                    USING TRY_CAST({col} AS DOUBLE);
                """)
                print(f"colonne {col} de {table}_clean convertie en DOUBLE")
    conn.close()  
    return tables_clean