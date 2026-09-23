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
    


