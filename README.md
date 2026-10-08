#  BottleNeck – Automatisation ETL & Analyse de données / ETL Automation & Data Analysis

> Projet Data Engineer – Automatisation d'un pipeline de nettoyage, réconciliation et analyse de données de vente pour un marchand de vin.
> Data Engineer project – Automation of a cleaning, reconciliation and analysis pipeline for a wine merchant's sales data.

---

## 🇫🇷 Français

### Contexte

BottleNeck est un marchand de vin qui dispose de deux systèmes sources : un **CMS** (site web) et un **ERP**. Un premier travail manuel d'analyse (nettoyage, réconciliation, calcul du chiffre d'affaires, identification des vins premium via le z-score) avait été réalisé par un data analyst. L'objectif de ce projet est **d'automatiser l'ensemble de cette chaîne de traitement** afin que les équipes produit reçoivent chaque mois, sans intervention manuelle :

- un rapport du chiffre d'affaires (par produit et global) ;
- un extrait des vins **premium** ;
- un extrait des vins **ordinaires**.

### Ce que fait le pipeline

1. **Extraction** des trois fichiers sources (`erp.xlsx`, `liaison.xlsx`, `web.xlsx`) et chargement dans une base **DuckDB**.
2. **Nettoyage générique** : suppression des doublons, des colonnes/lignes entièrement vides, harmonisation des formats (dates, nombres, texte).
3. **Nettoyage métier** : suppression des prix négatifs ou nuls, des lignes de type "attachment" (images), des lignes sans SKU.
4. **Tests de qualité** après chaque étape (format, unicité, valeurs nulles) via **pytest**.
5. **Fusion** des tables ERP et Web via la table de liaison, avec vérification du nombre de lignes avant/après jointure.
6. **Calcul du chiffre d'affaires** par produit et global, avec test de cohérence (somme des CA produits = CA global).
7. **Calcul du z-score** sur le prix des vins pour classer chaque produit en **premium** ou **ordinaire**.
8. **Export** des résultats :
   - un fichier Excel du chiffre d'affaires (deux feuilles : `CA_products` et `CA_global`) ;
   - deux fichiers CSV séparés (`vins_premium.csv`, `vins_ordinaires.csv`).
9. **Orchestration** de l'ensemble du flux avec **Kestra**, incluant une version avec boucles de re-test automatique (`LoopUntil`) et mise en pause en cas d'échec d'un test, ainsi qu'une parallélisation des exports finaux.

### Architecture (Data Lineage)

L'architecture complète du pipeline (import → nettoyage → tests → jointure → calcul du CA → z-score → exports) est détaillée ci-dessous sous forme de diagramme Mermaid, avec à chaque étape critique un point de contrôle qualité et une boucle de correction en cas d'échec.

```mermaid

flowchart TD;
  DT[("Database")]
  e1["Import des données<br/>- erp.xlsx<br/>- liaison.xlsx<br/>- web.xlsx"]
  d1@{ shape: lean-r, label: "Données exportées" }
  A["Nettoyage:<br/>- suppression doublons<br/>- colonnes vides<br/>- lignes vides<br/>- formatage (date, texte, entiers...)"]
  d2@{ shape: lean-r, label: "Données nettoyées" }
  T1["Tests:<br/>- format de données,<br/>- unicité,<br/>- colonnes ou lignes vides"]
  c1{"Tests OK?"}
  V1["Vérifier les données"]
  B["Jointure:<br/>Jonction des tables erp et web<br/>via la table liaison"]
  d3@{ shape: lean-r, label: "Table Fusion" }
  T2["Tests:<br/>comparaison du nombre de lignes avant et après jonction"]
  c2{"Tests OK?"}
  V2["Vérifier les données"]
  C["Calcul du chiffre d'affaires (CA):<br/>- par vin,<br/>- total"]
  T3["Test de cohérence du CA:<br/>sommes des CA par vin vs CA total"]
  c3{"CA cohérent?"}
  V3["Vérifier les données"]
  D["Calcul du z-score sur le prix des vins"]
  E["Extraction rapport en Excel"]
  s1@{shape: doc, label: "Extrait CA par produit et total<br/>(fichier Excel)"}
  T4["Test de cohérence:<br/>z-score vs catégorie vin premium/vin ordinaire"]
  c4{"Test OK?"}
  V4["Vérifier les prix incohérents"]
  F["Séparation des données vins premium/ordinaires"]
  G-1["Extraction des données"]
  G-2["Extraction des données"]
  d4@{ shape: lean-r, label: "données vins premium" }
  d5@{ shape: lean-r, label: "données vins secondaires" }
  s2@{shape: doc, label: "Extrait vins premium<br/>(fichier CSV)"}
  s3@{shape: doc, label: "Extrait vins secondaires<br/>(fichier CSV)"}
  fin@{shape: terminal, label: "fin"}

  DT-->e1;
  e1-->d1;
  d1-->A;
  A-->d2;
  d2-->T1;
  T1-->c1;
  c1-->|"non"|V1;
  c1-->|"oui"| B;  
  V1-->A;  
  B-->d3;
  d3-->T2;
  T2-->c2;
  c2-->|"non"| V2;
  c2-->|"oui"| C;
  V2-->B;
  C-->T3;
  T3-->c3;
  c3-->|"non"| V3;
  c3-->|"oui"| D;
  c3--"oui"--> E;
  V3-->C;
  E-->s1;
  D-->T4;
  T4-->c4;
  c4-->|"non"| V4;
  c4-->|"oui"| F;
  V4-->D;
  F-->d4;
  F-->d5;
  d4-->G-1;
  d5-->G-2;
  G-1-->s2;
  G-2-->s3;
  s2-->fin;
  s3-->fin;
  
  style T1 fill:#fdebd0,stroke:#e67e22
  style T2 fill:#fdebd0,stroke:#e67e22
  style T3 fill:#fdebd0,stroke:#e67e22
  style T4 fill:#fdebd0,stroke:#e67e22
  style e1 fill:#d6eaf8,stroke:#2980b9
  style A fill:#d6eaf8,stroke:#2980b9  
  style B fill:#d6eaf8,stroke:#2980b9
  style C fill:#d6eaf8,stroke:#2980b9
  style D fill:#d6eaf8,stroke:#2980b9  
  style E fill:#d6eaf8,stroke:#2980b9
  style F fill:#d6eaf8,stroke:#2980b9
  style G-1 fill:#d6eaf8,stroke:#2980b9
  style G-2 fill:#d6eaf8,stroke:#2980b9
  style d1 fill:#d5f5e3,stroke:#27ae60
  style d2 fill:#d5f5e3,stroke:#27ae60
  style d3 fill:#d5f5e3,stroke:#27ae60
  style d4 fill:#d5f5e3,stroke:#27ae60
  style d5 fill:#d5f5e3,stroke:#27ae60
  style c1 fill:#ffdfe5,stroke:#ff5978
  style c2 fill:#ffdfe5,stroke:#ff5978
  style c3 fill:#ffdfe5,stroke:#ff5978
  style c4 fill:#ffdfe5,stroke:#ff5978
```

### Stack technique

| Outil | Rôle |
|---|---|
| **Python** | Scripts de traitement des données |
| **DuckDB** | Base de données analytique locale, requêtée en SQL |
| **pandas / openpyxl** | Calculs et export Excel multi-feuilles |
| **pytest** | Tests automatisés de qualité des données à chaque étape |
| **Kestra** | Orchestrateur de workflow (installation via Docker) |
| **Jupyter Notebook** | Développement, documentation et démonstration du pipeline |

### Installation

Le fichier `requirements.txt` fourni dans le dépôt permet d'installer toutes les dépendances Python nécessaires.

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd <nom-du-depot>

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate      # sous Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Orchestration avec Kestra

Pour exécuter le pipeline complet via Kestra :

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/kestra-io/kestra/refs/heads/develop/docker-compose.yml
docker compose up -d
```

Puis se rendre sur [http://localhost:8080](http://localhost:8080) pour créer un compte administrateur et importer les flows YAML fournis (version simple et version avec tests intégrés).

**Visualisation du workflow Kestra final**

![flow-graph.jpeg](flow-graph.jpeg)


### Utilisation

- Ouvrir le notebook (`notebook_projet_10.ipynb`) avec Jupyter pour suivre pas à pas la construction du pipeline, tester les scripts en local avec DuckDB, et consulter les résultats intermédiaires.
- Les scripts unitaires (nettoyage, fusion, calcul du CA, z-score) et les scripts de tests `pytest` se trouvent dans les dossiers `scripts/` et `tests/` et sont directement réutilisés par les flows Kestra.
- Le fichier `conftest.py` centralise les fixtures pytest et renvoie automatiquement le résultat des tests à Kestra via `Kestra.outputs()`.

### Tests

Les tests couvrent :
- l'absence de colonnes/lignes entièrement nulles ;
- l'absence de prix négatifs, de lignes "attachment" ou de SKU manquant ;
- la cohérence du nombre de lignes après jointure ERP/Web ;
- la cohérence du chiffre d'affaires (somme par produit = total) ;
- la cohérence de la classification premium/ordinaire par rapport au z-score.

Lancer les tests avec :
```bash
pytest
```
### Visualisation dans PowerBI

**Tables chargées**<br>
![Tables_PowerBI.png](Tables_PowerBI.png)

**Dashboard** <br>
![Dashboard_PowerBI.png](Dashboard_PowerBI.png)
---

## 🇬🇧 English

### Context

BottleNeck is a wine merchant with two source systems: a **CMS** (website) and an **ERP**. A data analyst had already performed a first manual analysis (cleaning, reconciliation, revenue calculation, premium wine identification using the z-score). The goal of this project is to **automate this entire processing chain** so that product teams receive, every month, without any manual intervention:

- a revenue report (per product and total);
- an extract of **premium** wines;
- an extract of **regular** wines.

### What the pipeline does

1. **Extraction** of the three source files (`erp.xlsx`, `liaison.xlsx`, `web.xlsx`) and loading into a **DuckDB** database.
2. **Generic cleaning**: removal of duplicates, fully empty columns/rows, and format harmonization (dates, numbers, text).
3. **Business-specific cleaning**: removal of negative or zero prices, "attachment" rows (images), and rows with a missing SKU.
4. **Quality tests** after each step (format, uniqueness, null values) using **pytest**.
5. **Merging** the ERP and Web tables through the linking table, with a row-count check before/after the join.
6. **Revenue calculation** per product and overall, with a consistency test (sum of per-product revenue = total revenue).
7. **Z-score calculation** on wine prices to classify each product as **premium** or **regular**.
8. **Export** of the results:
   - an Excel file with the revenue figures (two sheets: `CA_products` and `CA_global`);
   - two separate CSV files (`vins_premium.csv`, `vins_ordinaires.csv`).
9. **Orchestration** of the whole flow with **Kestra**, including a version with automatic retry loops (`LoopUntil`) that pauses the flow when a test fails, plus parallelized final exports.

### Architecture (Data Lineage)

The full pipeline architecture (import → cleaning → tests → join → revenue calculation → z-score → exports) is detailed hereafter as a Mermaid diagram, with a quality checkpoint and a correction loop at each critical step.

```mermaid

flowchart TD;
  DT[("Database")]
  e1["Data import<br/>- erp.xlsx<br/>- liaison.xlsx<br/>- web.xlsx"]
  d1@{ shape: lean-r, label: "Exported data" }
  A["Cleaning:<br/>- remove duplicates<br/>- empty columns<br/>- empty rows<br/>- formatting (date, text, integers...)"]
  d2@{ shape: lean-r, label: "Cleaned data" }
  T1["Tests:<br/>- data format,<br/>- uniqueness,<br/>- empty columns or rows"]
  c1{"Tests OK?"}
  V1["Check the data"]
  B["Join:<br/>Merge the erp and web tables<br/>via the liaison table"]
  d3@{ shape: lean-r, label: "Merged table" }
  T2["Tests:<br/>compare row count before and after join"]
  c2{"Tests OK?"}
  V2["Check the data"]
  C["Revenue calculation:<br/>- per wine,<br/>- total"]
  T3["Revenue consistency test:<br/>sum of revenue per wine vs total revenue"]
  c3{"Revenue consistent?"}
  V3["Check the data"]
  D["Z-score calculation on wine prices"]
  E["Export report to Excel"]
  s1@{shape: doc, label: "Revenue extract by product and total<br/>(Excel file)"}
  T4["Consistency test:<br/>z-score vs premium wine / ordinary wine category"]
  c4{"Test OK?"}
  V4["Check inconsistent prices"]
  F["Split premium / ordinary wine data"]
  G-1["Data extraction"]
  G-2["Data extraction"]
  d4@{ shape: lean-r, label: "Premium wine data" }
  d5@{ shape: lean-r, label: "Secondary wine data" }
  s2@{shape: doc, label: "Premium wine extract<br/>(CSV file)"}
  s3@{shape: doc, label: "Secondary wine extract<br/>(CSV file)"}
  fin@{shape: terminal, label: "end"}

  DT-->e1;
  e1-->d1;
  d1-->A;
  A-->d2;
  d2-->T1;
  T1-->c1;
  c1-->|"no"|V1;
  c1-->|"yes"| B;  
  V1-->A;  
  B-->d3;
  d3-->T2;
  T2-->c2;
  c2-->|"no"| V2;
  c2-->|"yes"| C;
  V2-->B;
  C-->T3;
  T3-->c3;
  c3-->|"no"| V3;
  c3-->|"yes"| D;
  c3--"yes"--> E;
  V3-->C;
  E-->s1;
  D-->T4;
  T4-->c4;
  c4-->|"no"| V4;
  c4-->|"yes"| F;
  V4-->D;
  F-->d4;
  F-->d5;
  d4-->G-1;
  d5-->G-2;
  G-1-->s2;
  G-2-->s3;
  s2-->fin;
  s3-->fin;
  
  style T1 fill:#fdebd0,stroke:#e67e22
  style T2 fill:#fdebd0,stroke:#e67e22
  style T3 fill:#fdebd0,stroke:#e67e22
  style T4 fill:#fdebd0,stroke:#e67e22
  style e1 fill:#d6eaf8,stroke:#2980b9
  style A fill:#d6eaf8,stroke:#2980b9  
  style B fill:#d6eaf8,stroke:#2980b9
  style C fill:#d6eaf8,stroke:#2980b9
  style D fill:#d6eaf8,stroke:#2980b9  
  style E fill:#d6eaf8,stroke:#2980b9
  style F fill:#d6eaf8,stroke:#2980b9
  style G-1 fill:#d6eaf8,stroke:#2980b9
  style G-2 fill:#d6eaf8,stroke:#2980b9
  style d1 fill:#d5f5e3,stroke:#27ae60
  style d2 fill:#d5f5e3,stroke:#27ae60
  style d3 fill:#d5f5e3,stroke:#27ae60
  style d4 fill:#d5f5e3,stroke:#27ae60
  style d5 fill:#d5f5e3,stroke:#27ae60
  style c1 fill:#ffdfe5,stroke:#ff5978
  style c2 fill:#ffdfe5,stroke:#ff5978
  style c3 fill:#ffdfe5,stroke:#ff5978
  style c4 fill:#ffdfe5,stroke:#ff5978
```


### Tech stack

| Tool | Role |
|---|---|
| **Python** | Data processing scripts |
| **DuckDB** | Local analytical database, queried in SQL |
| **pandas / openpyxl** | Calculations and multi-sheet Excel export |
| **pytest** | Automated data-quality tests at each step |
| **Kestra** | Workflow orchestrator (installed via Docker) |
| **Jupyter Notebook** | Development, documentation and demonstration of the pipeline |

### Installation

The `requirements.txt` file included in the repository lets you install all the required Python dependencies.

```bash
# 1. Clone the repository
git clone <repo-url>
cd <repo-name>

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Orchestration with Kestra 

To run the full pipeline through Kestra:

```bash
curl -o docker-compose.yml https://raw.githubusercontent.com/kestra-io/kestra/refs/heads/develop/docker-compose.yml
docker compose up -d
```

Then go to [http://localhost:8080](http://localhost:8080) to create an admin account and import the provided YAML flows (simple version and version with integrated tests).

**Vizualisation of the final Kestra workflow**

![flow-graph.jpeg](flow-graph.jpeg)


### Usage

- Open the notebook (`notebook_projet_10.ipynb`) with Jupyter to follow the pipeline build step by step, test scripts locally with DuckDB, and review intermediate results.
- The individual scripts (cleaning, merging, revenue calculation, z-score) and the `pytest` test scripts live in the `scripts/` and `tests/` folders and are reused directly by the Kestra flows.
- The `conftest.py` file centralizes pytest fixtures and automatically reports test results back to Kestra via `Kestra.outputs()`.

### Tests

Tests cover:
- absence of fully null columns/rows;
- absence of negative prices, "attachment" rows, or missing SKUs;
- row-count consistency after the ERP/Web join;
- revenue consistency (sum per product = total);
- consistency of the premium/regular classification against the z-score.

Run the tests with:
```bash
pytest
```
### Visualization in PowerBI

**Imported Tables** <br>
![Tables_PowerBI.png](Tables_PowerBI.png)

**Dashboard** <br>
![Dashboard_PowerBI.png](Dashboard_PowerBI.png)
---

## Structure du projet / Project structure

```

│   bottleneck.team.bottleneck_duckdb_flow.yaml         # Flow Kestra simple / Basic Kestra flow
│   bottleneck.team.bottleneck_duckdb_flow_test.yaml    # Flow Kestra avec tests / Kestra flow with tests
│   docker-compose.yml                                  # Installation de Kestra / Kestra installation
│   Dockerfile                                          # Image Kestra custom (duckdb, pytest...) / Custom Kestra image (duckdb, pytest...)
│   notebook_projet_10.ipynb                            # Notebook principal / Main notebook
│   README.md
│   requirements.txt                                    # Dépendances Python / Python dependencies
│
├───scripts                                             # Scripts de traitement utilisés par Kestra / Processing scripts used by Kestra
│       functions_cleaning_tables.py                    # Nettoyage générique / Generic cleaning
│       functions_specific_cleaning_tables.py           # Nettoyage métier / Business-specific cleaning
│       function_creation_tables.py                     # Création des tables DuckDB / DuckDB table creation
│       fusion_tables_liaison.py                        # Jointure ERP/Web/liaison / ERP/Web/linking table join
│       script_z_score.py                               # Calcul du z-score et classification / Z-score calculation and classification
│
└───tests                                                # Tests pytest / Pytest tests
        conftest.py                                     # Fixtures + reporting Kestra / Fixtures + Kestra reporting
        test_ca.py                                      # Test cohérence du chiffre d'affaires / Revenue consistency test
        test_cleaning.py                                # Test nettoyage générique / Generic cleaning test
        test_cleaning_specific.py                       # Test nettoyage métier / Business-specific cleaning test
        test_fusion_erp_web.py                          # Test de la jointure / Join test
        test_z_score.py                                 # Test du z-score / Z-score test
```
