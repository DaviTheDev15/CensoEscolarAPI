import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/municipios"
resposta = requests.get(url)

if resposta.status_code == 200:
    municipios = resposta.json()
    for i, municipio in enumerate(municipios):
        municipioN = {
            'CO_MUNICIPIO': municipio['id'],
            'NO_MUNICIPIO': municipio['nome'],
            'CO_MICRORREGIAO': municipio['microrregiao']['id']
        }
        municipios[i] = municipioN
    with open('MunicipiosNordeste.json', 'w', encoding='utf-8') as f:
        json.dump(municipios, f, ensure_ascii=False, indent=2)
    print("Os Municipios do Nordeste foram filtrados e salvos em um arquivo JSON.")
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)