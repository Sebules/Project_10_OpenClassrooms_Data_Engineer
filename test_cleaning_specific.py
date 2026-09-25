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

def test_bons_cadeau(conn):
    # Arrange
    table = 'web_export_data_clean'

    #Act
    rows_bons = conn.sql(f"SELECT * FROM {database}.{table} WHERE sku = 'bon-cadeau-25-euros';").fetchall()

    # Assert
    assert rows_bons==[], f" il y a des lignes bons-cadeau dans la table {table}"

def test_attachment(conn):
    # Arrange
    table = 'web_export_data_clean'

    #Act
    rows_attachment = conn.sql(f"SELECT * FROM {database}.{table} WHERE post_type = 'attachment';").fetchall()

    # Assert
    assert rows_attachment==[], f" il y a des lignes attachment dans la table {table}: {rows_attachment[0:2]}"

def test_sku_null(conn):
    # Arrange
    table = 'web_export_data_clean'

    #Act
    rows_sku = conn.sql(f"SELECT * FROM {database}.{table} WHERE sku IS NULL;").fetchall()

    # Assert
    assert rows_sku==[], f" il y a des lignes avec un sku null dans la table {table}: {rows_sku[0:2]}"

def test_negative_price(conn):
    # Arrange
    tables_clean = ["web_export_data_clean", "liaison_export_data_clean", "erp_export_data_clean"]

    # Act
    df_negative_price = []
    for table in tables_clean:
        describe = conn.sql(f"SELECT column_name FROM (DESCRIBE {database}.{table});")
        describe_columns = [row[0] for row in describe.fetchall()]

        if 'price' in describe_columns:
            row_negative_price=conn.sql(f"SELECT * FROM {database}.{table} WHERE TRY_CAST (price AS DOUBLE) <=0;").fetchall()
            df_negative_price.append((table, row_negative_price))
        else:
            pass

    # Assert
    for table, row in df_negative_price:
        assert row ==[], f" il y a des prix négatifs dans la table {table}: {row}"
    