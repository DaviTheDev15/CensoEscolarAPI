import requests
from psycopg2.extras import execute_values
from helpers.database import connect_raw
from helpers.logging import logger

URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Municipios (
    CO_MUNICIPIO     INTEGER PRIMARY KEY,
    NO_MUNICIPIO     TEXT NOT NULL,
    CO_MICRORREGIAO  INTEGER,
    FOREIGN KEY (CO_MICRORREGIAO) REFERENCES Microrregioes(CO_MICRORREGIAO)
);
"""

UPSERT_SQL = """
INSERT INTO Municipios (CO_MUNICIPIO, NO_MUNICIPIO, CO_MICRORREGIAO)
VALUES %s
ON CONFLICT (CO_MUNICIPIO) DO UPDATE
SET NO_MUNICIPIO    = EXCLUDED.NO_MUNICIPIO,
    CO_MICRORREGIAO = EXCLUDED.CO_MICRORREGIAO;
"""

resposta = requests.get(URL)
if resposta.status_code != 200:
    logger.error("Erro ao acessar a API: %s", resposta.status_code)

todos_municipios = resposta.json()
rows = []

for municipio in todos_municipios:
    microrregiao = municipio.get('microrregiao')
    rows.append((
        municipio.get('id'),
        municipio.get('nome'),
        microrregiao.get('id') if microrregiao else None
    ))

if not rows:
    logger.warning("Nenhum município encontrado.")

conn = connect_raw()
try:
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)
        execute_values(cur, UPSERT_SQL, rows, page_size=1000)
    conn.commit()
    print("A tabela Municipios foi inserida/atualizada no Postgres com sucesso.")
except Exception:
    conn.rollback()
    logger.exception("Erro ao persistir a tabela Municipios no banco")
finally:
    conn.close()