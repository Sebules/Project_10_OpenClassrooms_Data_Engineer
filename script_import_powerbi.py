import duckdb
import urllib.request
import tempfile, os, shutil

url = "https://raw.githubusercontent.com/Sebules/Project_10_OpenClassrooms_Data_Engineer/export/exports/bottleneck.db"
tmpdir = tempfile.mkdtemp()  # dossier unique à chaque exécution
path = os.path.join(tempfile.gettempdir(), "bottleneck.db") # chemin de destination (dossier temporaire du système)
urllib.request.urlretrieve(url, path) # téléchargement du fichier de Github vers le dossier temporaire

con = duckdb.connect(path, read_only=True)
try:
    revenus_web = con.sql("SELECT * FROM revenus_web").df()
    web_erp_joined_z = con.sql("SELECT * FROM web_erp_joined_z").df()
    web_export_data_clean = con.sql("SELECT * FROM web_export_data_clean").df()
    erp_export_data_clean = con.sql("SELECT * FROM erp_export_data_clean").df()
    liaison_export_data_clean = con.sql("SELECT * FROM liaison_export_data_clean").df()
finally:
    con.close()
    shutil.rmtree(tmpdir, ignore_errors=True)  # nettoyage