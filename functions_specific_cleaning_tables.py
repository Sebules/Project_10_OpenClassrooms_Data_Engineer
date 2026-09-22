import duckdb

# Suppression et mise à part des produits avec un prix négatifs
def delete_negative_price(tables,tables_clean, database):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    tables_negative_prices = []
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
        
        if 'price' in describe_columns:
            conn.sql(f"DELETE FROM {database}.{table}_clean WHERE TRY_CAST(price AS DOUBLE) <=0;")
            conn.sql(f"CREATE OR REPLACE TABLE {database}.{table}_negative_prices AS SELECT * FROM {database}.{table} WHERE TRY_CAST(price AS DOUBLE) <=0;")
            print(conn.sql(f"SELECT * FROM {database}.{table}_negative_prices LIMIT 5"))
            tables_negative_prices.append(f"{table}_negative_prices")
            print(conn.sql(f"SELECT * FROM (SUMMARIZE {database}.{table}_clean) WHERE column_name = 'price'" ))
            
        else:
            print(f"no price column in table {table}")

    conn.close()
    return tables_clean, tables_negative_prices


# Suppression de lignes spécifiques
def suppression_lignes(tables_clean,database='bottleneck', column='sku',valeur='bon-cadeau-25-euros'):
    conn = duckdb.connect()
    conn.sql(f"ATTACH IF NOT EXISTS '{database}.db';")
    for table in tables_clean:
        describe = conn.sql(f"SELECT column_name FROM (DESCRIBE {database}.{table});")
        describe_columns = [row[0] for row in describe.fetchall()]
        if column in describe_columns:
            print("nombre de lignes avant suppression: \n" )
            print(conn.sql(f"SELECT COUNT(*) FROM {database}.{table};"))
            conn.sql(f"""
                DELETE FROM {database}.{table}
                WHERE {column} = {valeur};
                """)
            print("nombre de lignes après suppression:\n" )
            print(conn.sql(f"SELECT COUNT(*) FROM {database}.{table};"))
        else:
            print(f"La colonne {column} n'est pas dans la table {table}")

    conn.close()
    return tables_clean
