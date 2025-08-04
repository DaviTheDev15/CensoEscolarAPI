import requests
from psycopg2.extras import execute_values
from helpers.database import connect_raw
from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Microrregioes (
    CO_MICRORREGIAO INTEGER PRIMARY KEY,
    NO_MICRORREGIAO TEXT NOT NULL,
    CO_MESORREGIAO INTEGER NOT NULL,
    FOREIGN KEY (CO_MESORREGIAO) REFERENCES Mesorregioes(CO_MESORREGIAO)
);
"""

UPSERT_SQL = """
INSERT INTO Microrregioes (CO_MICRORREGIAO, NO_MICRORREGIAO, CO_MESORREGIAO)
VALUES %s
ON CONFLICT (CO_MICRORREGIAO) DO UPDATE
SET NO_MICRORREGIAO = EXCLUDED.NO_MICRORREGIAO,
    CO_MESORREGIAO = EXCLUDED.CO_MESORREGIAO;
"""

resposta = requests.get(url)
if resposta.status_code != 200:
    logger.error("Erro ao acessar a API: %s", resposta.status_code)

todas_microrregioes = resposta.json()
regioes = {1, 2, 3, 4, 5}

rows = [
    (
        microrregiao['id'],
        microrregiao['nome'],
        microrregiao['mesorregiao']['id']
    )
    for microrregiao in todas_microrregioes
    if microrregiao['mesorregiao']['UF']['regiao']['id'] in regioes
]

if not rows:
    logger.warning("Nenhuma microrregiao válida encontrada.")

conn = connect_raw()
try:
    with conn.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        execute_values(cursor, UPSERT_SQL, rows, page_size=1000)
    conn.commit()
    print("A tabela Microrregiaos foi inserida/atualizada no Postgres com sucesso.")
except Exception:
    conn.rollback()
    logger.exception("Erro ao persistir a tabela Microrregiaos no banco")
finally:
    conn.close()
