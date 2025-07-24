import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
resposta = requests.get(url)

if resposta.status_code == 200:
    todos_municipios = resposta.json()
    for i, municipio in enumerate(todos_municipios):
        microrregiao = municipio.get('microrregiao')
        municipioEditado = {
            'CO_MUNICIPIO': municipio.get('id'),
            'NO_MUNICIPIO': municipio.get('nome'),
            'CO_MICRORREGIAO': microrregiao.get('id') if microrregiao else None
        }
        todos_municipios[i] = municipioEditado

    with open('MunicipiosBrasil.json', 'w', encoding='utf-8') as f:
        json.dump(todos_municipios, f, ensure_ascii=False, indent=2)

    print("Os Municípios do Brasil foram filtrados e salvos em um arquivo JSON.")
else:
    logger.error("Erro ao acessar a API: %s", resposta.status_code)
