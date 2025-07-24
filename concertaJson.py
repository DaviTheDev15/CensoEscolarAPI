import json

ARQUIVO_ORIGINAL = 'instituicoes2024.json'
ARQUIVO_CORRIGIDO = 'instituicoes2024_corrigido.json'

with open(ARQUIVO_ORIGINAL, 'r', encoding='utf-8') as f:
    dados = json.load(f)

for item in dados:
    co_uf = str(item.get('CO_UF')).zfill(2)

    #CO_MESORREGIAO 4 dígitos
    co_meso = str(item.get('CO_MESORREGIAO')).zfill(2)
    item['CO_MESORREGIAO'] = int(co_uf + co_meso)

    #CO_MICRORREGIAO 5 dígitos
    co_micro = str(item.get('CO_MICRORREGIAO')).zfill(3)
    item['CO_MICRORREGIAO'] = int(co_uf + co_micro)

with open(ARQUIVO_CORRIGIDO, 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print(f"Arquivo corrigido salvo como: {ARQUIVO_CORRIGIDO}")
