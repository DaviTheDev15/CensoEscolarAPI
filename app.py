from flask import Flask, jsonify, request
import json

app = Flask(__name__)

def loadData():
    with open('instituicoes.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def saveData(instituicoes):
    with open('instituicoes.json', 'w', encoding='utf-8') as f:
        json.dump(instituicoes, f, ensure_ascii=False, indent=4)


@app.route('/instituicoesensino', methods=['GET'])
def getInstituicoes():
    instituicoes = loadData()
    return jsonify(instituicoes)


@app.route('/instituicoesensino/<co_entidade>', methods=['GET'])
def getInstituicao(co_entidade):
    instituicoes = loadData()
    try:
        co_entidade = int(co_entidade)
    except ValueError:
        return jsonify({"erro": "Código da entidade inválido!"}), 400
    instituicao = next((item for item in instituicoes if item["CO_ENTIDADE"] == co_entidade), None)
    if instituicao:
        return jsonify(instituicao)
    else:
        return jsonify({"erro": "Instituição não encontrada!"}), 404


@app.route('/instituicoesensino', methods=['POST'])
def createInstituicao():
    newInstituicao = request.json
    instituicoes = loadData()
    instituicoes.append(newInstituicao)
    saveData(instituicoes)
    return jsonify(newInstituicao), 201


@app.route('/instituicoesensino/<co_entidade>', methods=['PUT'])
def updateData(co_entidade):
    instituicoes = loadData()
    try:
        co_entidade = int(co_entidade)
    except ValueError:
        return jsonify({"erro": "Código da entidade inválido!"}), 400
    instituicao = next((item for item in instituicoes if item["CO_ENTIDADE"] == co_entidade), None)
    if instituicao:
        newDatas = request.json
        instituicao.update(newDatas)
        saveData(instituicoes)
        return jsonify(instituicao)
    else:
        return jsonify({"erro": "Instituição não encontrada!"}), 404


@app.route('/instituicoesensino/<co_entidade>', methods=['DELETE'])
def deleteData(co_entidade):
    instituicoes = loadData()
    try:
        co_entidade = int(co_entidade)
    except ValueError:
        return jsonify({"erro": "Código da entidade inválido!"}), 400
    instituicoesAtualizada = [item for item in instituicoes if item["CO_ENTIDADE"] != co_entidade]
    if len(instituicoes) == len(instituicoesAtualizada):
        return jsonify({"erro": "Instituição não encontrada!"}), 404
    saveData(instituicoesAtualizada)
    return jsonify({"mensagem": "Instituição deletada com sucesso!"})


if __name__ == '__main__':
    app.run(debug=True)