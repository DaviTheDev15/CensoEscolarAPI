import json
import subprocess
import sys
from psycopg2.extras import execute_values
from helpers.database import connect_raw
from helpers.logging import logger

#teste

EXTRATORS = [
    "UFExtrator.py",
    "MesorregiaoExtrator.py",
    "MicrorregiaoExtrator.py",
    "MunicipioExtrator.py",
]

def run_script(script_name):
    print(f"Executando {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar {script_name}:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout)


def run_schemas():
    conn = connect_raw()
    try:
        with conn.cursor() as cur:
            with open("schemas.sql", "r", encoding="utf-8") as sql_file:
                sql_script = sql_file.read()
                cur.execute(sql_script) 
        conn.commit()
        print("Tabela criadas conforme schemas.sql.")
    except Exception:
        conn.rollback()
        logger.exception("Erro ao executar schemas.sql")
        sys.exit(1)
    finally:
        conn.close()


for script in EXTRATORS:
    run_script(script)

run_schemas()


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Instituicoes (
    NU_ANO_CENSO    INTEGER,
    CO_ENTIDADE     BIGINT NOT NULL,
    NO_ENTIDADE     TEXT NOT NULL,
    NO_REGIAO       TEXT,
    CO_REGIAO       INTEGER,
    NO_UF           TEXT,
    SG_UF           TEXT,
    CO_UF           INTEGER,
    NO_MUNICIPIO    TEXT,
    CO_MUNICIPIO    INTEGER,
    CO_MESORREGIAO  INTEGER,
    CO_MICRORREGIAO INTEGER,
    QT_MAT_BAS      INTEGER,
    QT_MAT_EJA      INTEGER,
    QT_MAT_ESP      INTEGER,
    QT_MAT_FUND      INTEGER,
    QT_MAT_INF      INTEGER,
    QT_MAT_MED      INTEGER,
    QT_MAT_PROF     INTEGER,
    PRIMARY KEY (NU_ANO_CENSO, CO_ENTIDADE),
    FOREIGN KEY (CO_UF) REFERENCES UFs(CO_UF),
    FOREIGN KEY (CO_MUNICIPIO) REFERENCES Municipios(CO_MUNICIPIO),
    FOREIGN KEY (CO_MESORREGIAO) REFERENCES Mesorregioes(CO_MESORREGIAO),
    FOREIGN KEY (CO_MICRORREGIAO) REFERENCES Microrregioes(CO_MICRORREGIAO)
);
"""

UPSERT_SQL = """
INSERT INTO Instituicoes (
    NU_ANO_CENSO, CO_ENTIDADE, NO_ENTIDADE,NO_REGIAO, CO_REGIAO,
    NO_UF, SG_UF, CO_UF,
    NO_MUNICIPIO, CO_MUNICIPIO, CO_MESORREGIAO, CO_MICRORREGIAO,
    QT_MAT_BAS, QT_MAT_EJA, QT_MAT_ESP, QT_MAT_FUND,
    QT_MAT_INF, QT_MAT_MED, QT_MAT_PROF
) VALUES %s
ON CONFLICT (NU_ANO_CENSO,CO_ENTIDADE) DO UPDATE
SET NO_ENTIDADE    = EXCLUDED.NO_ENTIDADE,
    NO_REGIAO      = EXCLUDED.NO_REGIAO,
    CO_REGIAO      = EXCLUDED.CO_REGIAO,
    NO_UF          = EXCLUDED.NO_UF,
    SG_UF          = EXCLUDED.SG_UF,
    CO_UF          = EXCLUDED.CO_UF,
    NO_MUNICIPIO   = EXCLUDED.NO_MUNICIPIO,
    CO_MUNICIPIO   = EXCLUDED.CO_MUNICIPIO,
    CO_MESORREGIAO = EXCLUDED.CO_MESORREGIAO,
    CO_MICRORREGIAO= EXCLUDED.CO_MICRORREGIAO,
    QT_MAT_BAS     = EXCLUDED.QT_MAT_BAS,
    QT_MAT_EJA     = EXCLUDED.QT_MAT_EJA,
    QT_MAT_ESP     = EXCLUDED.QT_MAT_ESP,
    QT_MAT_FUND    = EXCLUDED.QT_MAT_FUND,
    QT_MAT_INF     = EXCLUDED.QT_MAT_INF,
    QT_MAT_MED     = EXCLUDED.QT_MAT_MED,
    QT_MAT_PROF    = EXCLUDED.QT_MAT_PROF;
"""

def chunked(data, size=5000):
    for i in range(0, len(data), size):
        yield data[i:i+size]

try:
    with open("instituicoes2023.json", "r", encoding="utf-8") as f:
        instituicoes = json.load(f)
except FileNotFoundError:
    logger.error("Arquivo instituicoes2024.json não encontrado.")
    exit(1)

rows = [
    (
        instituicoes['NU_ANO_CENSO'], instituicoes['CO_ENTIDADE'],
        instituicoes['NO_ENTIDADE'], instituicoes['NO_REGIAO'], instituicoes['CO_REGIAO'], instituicoes['NO_UF'], instituicoes['SG_UF'], instituicoes['CO_UF'],
        instituicoes['NO_MUNICIPIO'], instituicoes['CO_MUNICIPIO'], instituicoes['CO_MESORREGIAO'], 
        instituicoes['CO_MICRORREGIAO'],
        instituicoes.get('QT_MAT_BAS'), instituicoes.get('QT_MAT_EJA'), instituicoes.get('QT_MAT_ESP'),
        instituicoes.get('QT_MAT_FUND'), instituicoes.get('QT_MAT_INF'), instituicoes.get('QT_MAT_MED'),
        instituicoes.get('QT_MAT_PROF')
    )
    for instituicoes in instituicoes
]

if not rows:
    logger.warning("Nenhuma instituição encontrada.")

conn = connect_raw()
try:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        for batch in chunked(rows, 5000):
            execute_values(cur, UPSERT_SQL, batch, page_size=5000)
    conn.commit()
    print("Tabela instituicoes inserida/atualizada com sucesso.")
except Exception:
    conn.rollback()
    logger.exception("Erro ao persistir a tabela instituicoes no banco")
finally:
    conn.close()