import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes"
resposta = requests.get(url)

if resposta.status_code == 200:
    microrregioes = resposta.json()
    microrregioes_nordeste = [
        micro for micro in microrregioes
        if micro['mesorregiao']['UF']['regiao']['id'] == 2
    ]
    for i, microrregiao in enumerate(microrregioes_nordeste):
        microrregiaoN = {
            'CO_MICRORREGIAO': microrregiao['id'],
            'NO_MICRORREGIAO': microrregiao['nome'],
            'CO_MESORREGIAO': microrregiao['mesorregiao']['id']
        }
        microrregioes_nordeste[i] = microrregiaoN
    with open('MicrorregiaoNordeste.json', 'w', encoding='utf-8') as f:
        json.dump(microrregioes_nordeste, f, ensure_ascii=False, indent=2)
    print('As Microrregiões do Nordeste foram filtradas e salvas em um arquivo JSON.')
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)