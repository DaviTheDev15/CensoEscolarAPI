import requests
from psycopg2.extras import execute_values
from helpers.database import connect_raw
from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS Mesorregioes (
    CO_MESORREGIAO INTEGER PRIMARY KEY,
    NO_MESORREGIAO TEXT NOT NULL,
    CO_UF INTEGER NOT NULL,
    FOREIGN KEY (CO_UF) REFERENCES UFs(CO_UF)
);
"""

UPSERT_SQL = """
INSERT INTO Mesorregioes (CO_MESORREGIAO, NO_MESORREGIAO, CO_UF)
VALUES %s
ON CONFLICT (CO_MESORREGIAO) DO UPDATE
SET NO_MESORREGIAO = EXCLUDED.NO_MESORREGIAO,
    CO_UF = EXCLUDED.CO_UF;
"""

resposta = requests.get(url)
if resposta.status_code != 200:
    logger.error("Erro ao acessar a API: %s", resposta.status_code)

todas_mesorregioes = resposta.json()

regioes_validas = {1, 2, 3, 4, 5}
rows = [
    (
        messoregiao['id'],           
        messoregiao['nome'],         
        messoregiao['UF']['id']      
    )
    for messoregiao in todas_mesorregioes
    if messoregiao['UF']['regiao']['id'] in regioes_validas
]

if not rows:
    logger.warning("Nenhuma mesorregião válida encontrada.")

conn = connect_raw()
try:
    with conn.cursor() as cursor:
        cursor.execute(CREATE_TABLE_SQL)
        execute_values(cursor, UPSERT_SQL, rows, page_size=1000)
    conn.commit()
    print("A tabela Mesorregioes foi inserida/atualizada no Postgres com sucesso.")
except Exception:
    conn.rollback()
    logger.exception("Erro ao persistir a tabela Mesorregioes no banco")
finally:
    conn.close()
