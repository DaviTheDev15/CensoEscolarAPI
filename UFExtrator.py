import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes/2/estados"
resposta = requests.get(url)

if resposta.status_code == 200:
    ufs = resposta.json()
    for i, uf in enumerate(ufs):
        ufN = {
            'CO_UF': uf['id'],
            'SG_UF': uf['sigla'],
            'NO_UF': uf['nome']
        }
        ufs[i] = ufN
    with open('UFsNordeste.json', 'w', encoding='utf-8') as f:
        json.dump(ufs, f, ensure_ascii=False, indent=2)
    print("As UFs do Nordeste foram filtrados e salvos em um arquivo JSON.")
else:
    logger.error("Erro ao acessar a API:", resposta.status_code)