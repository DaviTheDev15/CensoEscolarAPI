import csv
import json

arquivoCSV = 'microdados2024.csv'

arquivoJSON = 'instituicoes2024.json'

coluna = 'SG_UF'
estados = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

colunas = [
"NO_REGIAO",
"CO_REGIAO",
"NO_UF",
"SG_UF",
"CO_UF",
"NO_MUNICIPIO",
"CO_MUNICIPIO",
"CO_MESORREGIAO",
"CO_MICRORREGIAO",
"NO_ENTIDADE",
"CO_ENTIDADE",
"QT_MAT_BAS",
"QT_MAT_EJA",
"QT_MAT_ESP",
"QT_MAT_FUND",
"QT_MAT_INF",
"QT_MAT_MED",
"QT_MAT_PROF"]

dadosFiltrados = []

with open(arquivoCSV, mode='r', encoding='latin-1') as csvArquivo:
    csvLeitor = csv.DictReader(csvArquivo, delimiter=';')
    for linha in csvLeitor:
        if linha[coluna] in estados:
            dados_extraidos = {}
            for campo in colunas:
                valor = linha[campo]
                if campo.startswith('NU_') or campo.startswith('CO_') or campo.startswith('QT_'):
                    try:
                        dados_extraidos[campo] = int(valor)
                    except ValueError:
                        dados_extraidos[campo] = None
                else:
                    dados_extraidos[campo] = valor
            dadosFiltrados.append(dados_extraidos)


jsonDados = json.dumps(dadosFiltrados, indent=4, ensure_ascii=False)
with open(arquivoJSON, mode='w', encoding='utf-8') as json_file:
    json_file.write(jsonDados)