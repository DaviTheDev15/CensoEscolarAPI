import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes"
resposta = requests.get(url)

if resposta.status_code == 200:
    todas_mesorregioes = resposta.json()
    mesorregioes_nordeste = []

    for mesorregiao in todas_mesorregioes:
        if mesorregiao['UF']['regiao']['id'] == 2:  # Nordeste
            mesorregiaoN = {
                'CO_MESORREGIAO': mesorregiao['id'],
                'NO_MESORREGIAO': mesorregiao['nome'],
                'CO_UF': mesorregiao['UF']['id']
            }
            mesorregioes_nordeste.append(mesorregiaoN)

    with open('MesorregioesNordeste.json', 'w', encoding='utf-8') as f:
        json.dump(mesorregioes_nordeste, f, ensure_ascii=False, indent=2)
    print('As Mesorregiões do Nordeste foram filtradas e salvas em um arquivo JSON.')
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)