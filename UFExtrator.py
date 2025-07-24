import requests
import json

from helpers.logging import logger

url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
resposta = requests.get(url)

if resposta.status_code == 200:
    ufs = resposta.json()
    for i, uf in enumerate(ufs):
        ufN = {
            'CO_UF': uf.get('id'),
            'SG_UF': uf.get('sigla'),
            'NO_UF': uf.get('nome')
        }
        ufs[i] = ufN
    with open('UFsBrasil.json', 'w', encoding='utf-8') as f:
        json.dump(ufs, f, ensure_ascii=False, indent=2)
    print("Todas as UFs do Brasil foram filtradas e salvas em um arquivo JSON.")
else:
    logger.error("Erro ao acessar a API: %s", resposta.status_code)
