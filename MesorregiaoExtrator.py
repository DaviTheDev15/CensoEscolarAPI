import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/mesorregioes"
resposta = requests.get(url)

if resposta.status_code == 200:
    todas_mesorregioes = resposta.json()
    messoregioesEditadas = []
    regioes = [1, 2, 3, 4, 5]

    for mesorregiao in todas_mesorregioes:
        if mesorregiao['UF']['regiao']['id'] in regioes:
            MesorregiaoEditada = {
                'CO_MESORREGIAO': mesorregiao['id'],
                'NO_MESORREGIAO': mesorregiao['nome'],
                'CO_UF': mesorregiao['UF']['id']
            }
            messoregioesEditadas.append(MesorregiaoEditada)

    with open('Mesorregioes2024.json', 'w', encoding='utf-8') as f:
        json.dump(messoregioesEditadas, f, ensure_ascii=False, indent=2)
    print('As Mesorregiões de 2024 foram filtradas e salvas em um arquivo JSON.')
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)