import requests
from helpers.logging import logger
from psycopg2.extras import execute_values
from helpers.database import connect_raw


url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS UFs (
    CO_UF   INTEGER PRIMARY KEY,
    SG_UF   VARCHAR(2) NOT NULL,
    NO_UF   TEXT NOT NULL
);
"""

UPSERT_SQL = """
INSERT INTO UFs (CO_UF, SG_UF, NO_UF)
VALUES %s
ON CONFLICT (CO_UF) DO UPDATE
SET SG_UF = EXCLUDED.SG_UF,
    NO_UF = EXCLUDED.NO_UF;
"""

resposta = requests.get(url)
if resposta.status_code != 200:
    logger.error("Erro ao acessar a API do IBGE: %s", resposta.status_code)

todas_UFs = resposta.json()

rows = [
    (uf.get('id'), uf.get('sigla'), uf.get('nome'))
    for uf in todas_UFs
]

conn = connect_raw()
try:
    with conn.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        execute_values(cursor, UPSERT_SQL, rows, page_size=1000)
    conn.commit()
    print("A tabela UFs foi inserida/atualizada no Postgres com sucesso.")
except Exception:
    conn.rollback()
    logger.exception("Erro ao persistir A tabela UFs no banco")
finally:
    conn.close()
