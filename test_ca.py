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

def test_CA(conn):
    # Arrange
    table = 'revenus_web'

    #Act
    ca_product_total = conn.sql(f"SELECT SUM(CA_product) FROM {database}.{table}").fetchone()[0]
    ca_global = conn.sql("SELECT SUM(price*total_sales) FROM bottleneck.revenus_web;").fetchone()[0]

    # Assert
    assert ca_product_total == ca_global, f"Le total CA produit n'est pas égale au CA global"