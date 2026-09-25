import pytest
import duckdb
import pandas as pd


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


def test_z_score(conn):
    # Arrange
    table = 'erp_export_data_clean_z'

    #Act
    faux_ordinaire = conn.sql(f'SELECT * FROM {database}.{table} WHERE premium = 0 AND "z-score" > 2;').fetchall()
    faux_premium = conn.sql(f'SELECT * FROM {database}.{table} WHERE premium = 1 AND "z-score" < 2;').fetchall()

    #Assert
    assert faux_ordinaire ==[], f"incohérence du z-score pour les lignes suivantes: {faux_ordinaire}"
    assert faux_premium == [], f"incohérence du z-score pour les lignes suivantes: {faux_premium}"
