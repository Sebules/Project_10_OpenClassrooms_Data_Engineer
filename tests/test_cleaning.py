import pytest
import duckdb


database = 'bottleneck'

@pytest.fixture(scope="module")
def conn():
    """
    une fixture pytest qui ouvre une seule connexion, 
    fait l'ATTACH une seule fois, et la partage entre les tests 
    (avec un vrai close() garanti même en cas d'erreur, via yield).
    """
    connection = duckdb.connect()
    connection.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    yield connection
    connection.close()


def test_absence_columns_null(conn):
    # Arrange

    tables_clean = ["web_export_data_clean", "liaison_export_data_clean", "erp_export_data_clean"]

    # Act
    df_columns_null = []
    for table in tables_clean:
        columns_null = conn.sql(
            f"""
                SELECT column_name
                FROM (SUMMARIZE {database}.{table})
                WHERE (null_percentage = 100.0) OR (min = '0.0' AND max = '0.0') OR (min = '0' AND max = '0')
            """).fetchall()
        df_columns_null.append((table,columns_null))

    # Assert
    for table, columns_null in df_columns_null:
        assert columns_null==[], f"Il y a encore des colonnes entièrement nulles dans la table {table}, les voici: {columns_null}"


def test_absence_rows_null(conn):
    # Arrange
    
    tables_clean = ["web_export_data_clean", "liaison_export_data_clean", "erp_export_data_clean"]

    # Act
    df_idx_rows_null = []
    for table in tables_clean:
        idx_rows = conn.sql(f"""SELECT idx FROM (
        SELECT row_number() OVER () AS idx, *
        FROM {database}.{table}
        )
        WHERE COLUMNS(* EXCLUDE(idx)) IS NULL;
        """).fetchall()
        # ajout de row_number() afin d'avoir le numéro de chaque ligne de la table. 
        # EXCLUDE(idx) est nécessaire pour exclure cette colonne de la condition vue qu'elle ne sera pas nulle.
        df_idx_rows_null.append((table,idx_rows))

    # Assert
    for table, idx_rows in df_idx_rows_null:
        assert idx_rows ==[], f"Il y a encore des lignes entièrement nulles dans la table {table}, voici leur index: {idx_rowsl}"

def test_dedoublement(conn):
    # Arrange
    tables_clean = ["web_export_data_clean", "liaison_export_data_clean", "erp_export_data_clean"]

    #Act
    df_nb_rows = []
    for table in tables_clean:
        nb_rows = conn.sql(f"""
        SELECT COUNT(*)
        FROM {database}.{table}
        """).fetchone()[0]

        nb_rows_distinct = conn.sql(f"""
        SELECT DISTINCT COUNT(*)
        FROM {database}.{table}
        """).fetchone()[0]

        diff_rows = nb_rows -  nb_rows_distinct
        df_nb_rows.append((table,diff_rows))


    # Assert
    for table, diff_rows in df_nb_rows:
        assert diff_rows == 0, f"Il y a encore {diff_rows} lignes en doublons dans la table {table}"


def test_convert_format(conn):
    # Arrange
    tables_clean = ["web_export_data_clean", "liaison_export_data_clean", "erp_export_data_clean"]
    list_conv_date = ['date', 'post_modified']
    list_conv_num = ['price', 'quantity', 'total']

    # Act    
    for table in tables_clean:
        describe = conn.sql(f"SELECT column_name FROM (DESCRIBE {database}.{table});")
        describe_columns = [row[0] for row in describe.fetchall()]

        df_cols_date = []
        df_cols_num = []
        for col in describe_columns:
            col_lower = col.lower()

            if any(word in col_lower for word in list_conv_date):
                col_date = conn.sql(f"""SELECT column_name, column_type
                    FROM (DESCRIBE {database}.{table})
                    WHERE column_name = '{col}' ;
                    """).fetchall()
                df_cols_date.append((table, col_date[0][0], col_date[0][1]))
            
            if any(word in col_lower for word in list_conv_num):
                col_num = conn.sql(f"""SELECT column_name, column_type
                    FROM (DESCRIBE {database}.{table})
                    WHERE column_name = '{col}' ;
                    """).fetchall()
                df_cols_num.append((table, col_num[0][0], col_num[0][1]))

    # Assert
    for table, col_name, col_type in df_cols_date:
        assert col_type == "DATE", f"la colonne {col_name} dans la table {table} n'a pas le bon format (DATE)."
    for table, col_name, col_type in df_cols_num:
        assert col_type == "DOUBLE",  f"la colonne {col_name} dans la table {table} n'a pas le bon format (DOUBLE)."

        
       




        
     
    


