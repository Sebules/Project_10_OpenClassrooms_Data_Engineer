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

def test_fusion_erp_web(conn):
    # Arrange
    table = 'web_export_data_clean'
    table_fusion = 'web_erp_joined'

    # Act
    nb_row_web = conn.sql(f"SELECT COUNT(*) FROM {database}.{table}").fetchone()[0]
    nb_row_fusion = conn.sql(f"SELECT COUNT(*) FROM {database}.{table_fusion}").fetchone()[0]

    # Assert
    assert nb_row_web==nb_row_fusion, "La fusion des 2 tables erp et web n'est pas correcte."
