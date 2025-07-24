import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/microrregioes"
resposta = requests.get(url)

if resposta.status_code == 200:
    todas_microrregioes = resposta.json()
    regioes = [1, 2, 3, 4, 5]
    microrregioesEditadas = [
        micro for micro in todas_microrregioes
        if micro['mesorregiao']['UF']['regiao']['id'] in regioes
    ]
    for i, microrregiao in enumerate(microrregioesEditadas):
        microrregiaoEditada = {
            'CO_MICRORREGIAO': microrregiao['id'],
            'NO_MICRORREGIAO': microrregiao['nome'],
            'CO_MESORREGIAO': microrregiao['mesorregiao']['id']
        }
        microrregioesEditadas[i] = microrregiaoEditada
    with open('Microrregioes2024.json', 'w', encoding='utf-8') as f:
        json.dump(microrregioesEditadas, f, ensure_ascii=False, indent=2)
    print('As Microrregiões de 2024 foram filtradas e salvas em um arquivo JSON.')
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)