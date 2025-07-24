import sqlite3
import json

# Conectar/criar o banco de dados SQLite
conn = sqlite3.connect("CensoEscolarExtrator.db")
cursor = conn.cursor()

# 1. Criar as tabelas conforme schemas.sql
with open("schemas.sql", "r", encoding="utf-8") as sql_file:
    sql_script = sql_file.read()
    cursor.executescript(sql_script)

# 3. Inserir UFs
with open("UFsBrasil.json", "r", encoding="utf-8") as f:
    ufs = json.load(f)
for uf in ufs:
    cursor.execute(
        "INSERT OR IGNORE INTO UFs (CO_UF, SG_UF, NO_UF) VALUES (?, ?, ?)",
        (
            uf['CO_UF'],
            uf['SG_UF'],
            uf['NO_UF'],
        )
    )


# 5. Inserir Mesorregiões
with open("Mesorregioes2024.json", "r", encoding="utf-8") as f:
    mesorregioes = json.load(f)
for mesorregiao in mesorregioes:
    cursor.execute(
        "INSERT OR IGNORE INTO Mesorregioes (CO_MESORREGIAO, NO_MESORREGIAO, CO_UF) VALUES (?, ?, ?)",
        (
            mesorregiao['CO_MESORREGIAO'],
            mesorregiao['NO_MESORREGIAO'],
            mesorregiao['CO_UF']
        )
    )


# 6. Inserir Microrregiões
with open("Microrregioes2024.json", "r", encoding="utf-8") as f:
    microrregioes = json.load(f)
for microrregiao in microrregioes:
    cursor.execute(
        "INSERT OR IGNORE INTO Microrregioes (CO_MICRORREGIAO, NO_MICRORREGIAO, CO_MESORREGIAO) VALUES (?, ?, ?)",
        (
            microrregiao['CO_MICRORREGIAO'],
            microrregiao['NO_MICRORREGIAO'],
            microrregiao['CO_MESORREGIAO'],
        )
    )


# 4. Inserir Municípios
with open("MunicipiosBrasil.json", "r", encoding="utf-8") as f:
    municipios = json.load(f)
for municipio in municipios:
    cursor.execute(
        "INSERT OR IGNORE INTO Municipios (CO_MUNICIPIO, NO_MUNICIPIO, CO_MICRORREGIAO) VALUES (?, ?, ?)",
        (
            municipio['CO_MUNICIPIO'],
            municipio['NO_MUNICIPIO'],
            municipio['CO_MICRORREGIAO']
        )
    )



# 2. Inserir Instituições
with open("instituicoes2024_corrigido.json", "r", encoding="utf-8") as f:
    instituicoes = json.load(f)
for instituicao in instituicoes:
    cursor.execute(
        "INSERT INTO Instituicoes (\
            NO_REGIAO, CO_REGIAO, NO_UF, SG_UF, CO_UF,\
            NO_MUNICIPIO, CO_MUNICIPIO, CO_MESORREGIAO, \
            CO_MICRORREGIAO, NO_ENTIDADE, CO_ENTIDADE, QT_MAT_BAS, \
            QT_MAT_EJA, QT_MAT_ESP, QT_MAT_FUND, QT_MAT_INF, QT_MAT_MED, QT_MAT_PROF \
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            instituicao['NO_REGIAO'],
            instituicao['CO_REGIAO'],
            instituicao['NO_UF'],
            instituicao['SG_UF'],
            instituicao['CO_UF'],
            instituicao['NO_MUNICIPIO'],
            instituicao['CO_MUNICIPIO'],
            instituicao['CO_MESORREGIAO'],
            instituicao['CO_MICRORREGIAO'],
            instituicao['NO_ENTIDADE'],
            instituicao['CO_ENTIDADE'],
            instituicao.get('QT_MAT_BAS'),
            instituicao.get('QT_MAT_EJA'),
            instituicao.get('QT_MAT_ESP'),
            instituicao.get('QT_MAT_FUND'),
            instituicao.get('QT_MAT_INF'),
            instituicao.get('QT_MAT_MED'),
            instituicao.get('QT_MAT_PROF'),
        )
    )




# Commit e fechar conexão
conn.commit()
conn.close()
print("Banco 'CensoEscolarExtrator.db' inicializado com sucesso.")