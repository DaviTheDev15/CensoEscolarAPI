from flask import request, jsonify
import sqlite3
import math
from marshmallow import ValidationError

from helpers.application import app
from helpers.database import getConnection
from helpers.logging import logger
from helpers.CORS import cors

from models.InstituicaoEnsino import InstituicaoEnsino, InstituicaoEnsinoSchema

cors.init_app(app)

@app.route("/")
def index():
    versao = {"versao": "1.0.0"}
    return jsonify(versao), 200


@app.get("/instituicoes")
def getAll():
    logger.info("GET - Instituições")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))

    conn = getConnection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Instituicoes")
        total = cursor.fetchone()[0]
        pages = math.ceil(total / per_page) if per_page else 1
        offset = (page - 1) * per_page
        cursor.execute("SELECT * FROM Instituicoes LIMIT ? OFFSET ?", (per_page, offset))
        resultSet = cursor.fetchall()

        instituicoesEnsino = []
        for row in resultSet:
            instituicaoEnsino = InstituicaoEnsino(
                NO_REGIAO=row[0],
                CO_REGIAO=row[1],
                NO_UF=row[2],
                SG_UF=row[3],
                CO_UF=row[4],
                NO_MUNICIPIO=row[5],
                CO_MUNICIPIO=row[6],
                CO_MESORREGIAO=row[7],
                CO_MICRORREGIAO=row[8],
                NO_ENTIDADE=row[9],
                CO_ENTIDADE=row[10],
                QT_MAT_BAS=row[11],
                QT_MAT_EJA=row[12],
                QT_MAT_ESP=row[13],
                QT_MAT_FUND=row[14],
                QT_MAT_INF=row[15],
                QT_MAT_MED=row[16],
                QT_MAT_PROF=row[17],
            )
            instituicoesEnsino.append(instituicaoEnsino.toDict())

        return jsonify(instituicoesEnsino), 200


    except sqlite3.Error as e:
        logger.exception("Exception sqlite: %s", e)
        return jsonify({"ERROR": "Problema com o banco de dados."}), 500
    finally:
        conn.close()


@app.post("/instituicoes")
def post():
    logger.info("POST - Instituição")
    instituicaoEnsinoSchema = InstituicaoEnsinoSchema()
    instituicaoData = request.get_json()

    try:
        instituicaoJson = instituicaoEnsinoSchema.load(instituicaoData)

        conn = getConnection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Instituicoes
            (NO_REGIAO, CO_REGIAO, NO_UF, SG_UF, CO_UF,
             NO_MUNICIPIO, CO_MUNICIPIO, CO_MESORREGIAO, CO_MICRORREGIAO,
             NO_ENTIDADE, QT_MAT_BAS, QT_MAT_EJA, QT_MAT_ESP,
             QT_MAT_FUND, QT_MAT_INF, QT_MAT_MED, QT_MAT_PROF)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                instituicaoJson["NO_REGIAO"],
                instituicaoJson["CO_REGIAO"],
                instituicaoJson["NO_UF"],
                instituicaoJson["SG_UF"],
                instituicaoJson["CO_UF"],
                instituicaoJson["NO_MUNICIPIO"],
                instituicaoJson["CO_MUNICIPIO"],
                instituicaoJson["CO_MESORREGIAO"],
                instituicaoJson["CO_MICRORREGIAO"],
                instituicaoJson["NO_ENTIDADE"],
                instituicaoJson["QT_MAT_BAS"],
                instituicaoJson["QT_MAT_EJA"],
                instituicaoJson["QT_MAT_ESP"],
                instituicaoJson["QT_MAT_FUND"],
                instituicaoJson["QT_MAT_INF"],
                instituicaoJson["QT_MAT_MED"],
                instituicaoJson["QT_MAT_PROF"],
            ),
        )
        conn.commit()
        CO_ENTIDADE = cursor.lastrowid

        instituicaoEnsino = InstituicaoEnsino(
            instituicaoJson["NO_REGIAO"],
            instituicaoJson["CO_REGIAO"],
            instituicaoJson["NO_UF"],
            instituicaoJson["SG_UF"],
            instituicaoJson["CO_UF"],
            instituicaoJson["NO_MUNICIPIO"],
            instituicaoJson["CO_MUNICIPIO"],
            instituicaoJson["CO_MESORREGIAO"],
            instituicaoJson["CO_MICRORREGIAO"],
            instituicaoJson["NO_ENTIDADE"],
            CO_ENTIDADE,
            instituicaoJson["QT_MAT_BAS"],
            instituicaoJson["QT_MAT_EJA"],
            instituicaoJson["QT_MAT_ESP"],
            instituicaoJson["QT_MAT_FUND"],
            instituicaoJson["QT_MAT_INF"],
            instituicaoJson["QT_MAT_MED"],
            instituicaoJson["QT_MAT_PROF"],
        )

        return jsonify(instituicaoEnsino.toDict()), 201

    except ValidationError as err:
        return jsonify(err.messages), 400
    except sqlite3.Error as e:
        logger.exception("Exception sqlite: %s", e)
        return jsonify({"ERROR": "Problema com o banco de dados."}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.route("/instituicoes/<int:CO_ENTIDADE>", methods=["DELETE"])
def delete(CO_ENTIDADE):
    logger.info("DELETE - Instituição %s", CO_ENTIDADE)
    conn = getConnection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Instituicoes WHERE CO_ENTIDADE = ?", (CO_ENTIDADE,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"ERROR": "Instituição não encontrada."}), 404
        return jsonify({"mensagem": "Instituição removida com sucesso."}), 200
    except sqlite3.Error as e:
        logger.exception("Exception sqlite: %s", e)
        return jsonify({"ERROR": "Problema com o banco de dados."}), 500
    finally:
        conn.close()


@app.route("/instituicoes/<int:CO_ENTIDADE>", methods=["PUT"])
def put(CO_ENTIDADE):
    logger.info("PUT - Instituição %s", CO_ENTIDADE)
    conn = getConnection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Instituicoes WHERE CO_ENTIDADE = ?", (CO_ENTIDADE,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"ERROR": "Instituição não encontrada."}), 404

        instituicaoEnsinoSchema = InstituicaoEnsinoSchema()
        instituicaoData = request.get_json()
        instituicaoJson = instituicaoEnsinoSchema.load(instituicaoData)

        cursor.execute(
            """
            UPDATE Instituicoes
            SET NO_REGIAO = ?, CO_REGIAO = ?, NO_UF = ?, SG_UF = ?, CO_UF = ?,
                NO_MUNICIPIO = ?, CO_MUNICIPIO = ?, CO_MESORREGIAO = ?, CO_MICRORREGIAO = ?,
                NO_ENTIDADE = ?, QT_MAT_BAS = ?, QT_MAT_EJA = ?, QT_MAT_ESP = ?,
                QT_MAT_FUND = ?, QT_MAT_INF = ?, QT_MAT_MED = ?, QT_MAT_PROF = ?
            WHERE CO_ENTIDADE = ?
            """,
            (
                instituicaoJson["NO_REGIAO"],
                instituicaoJson["CO_REGIAO"],
                instituicaoJson["NO_UF"],
                instituicaoJson["SG_UF"],
                instituicaoJson["CO_UF"],
                instituicaoJson["NO_MUNICIPIO"],
                instituicaoJson["CO_MUNICIPIO"],
                instituicaoJson["CO_MESORREGIAO"],
                instituicaoJson["CO_MICRORREGIAO"],
                instituicaoJson["NO_ENTIDADE"],
                instituicaoJson["QT_MAT_BAS"],
                instituicaoJson["QT_MAT_EJA"],
                instituicaoJson["QT_MAT_ESP"],
                instituicaoJson["QT_MAT_FUND"],
                instituicaoJson["QT_MAT_INF"],
                instituicaoJson["QT_MAT_MED"],
                instituicaoJson["QT_MAT_PROF"],
                CO_ENTIDADE,
            ),
        )
        conn.commit()

        return jsonify({"mensagem": "Instituição atualizada com sucesso."}), 200

    except ValidationError as err:
        return jsonify(err.messages), 400
    except sqlite3.Error as e:
        logger.exception("Exception sqlite: %s", e)
        return jsonify({"ERROR": "Problema com o banco de dados."}), 500
    finally:
        conn.close()


@app.route("/instituicoes/<int:CO_ENTIDADE>", methods=["GET"])
def getById(CO_ENTIDADE):
    logger.info("GET - Instituição por CO_ENTIDADE = %s", CO_ENTIDADE)
    conn = getConnection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Instituicoes WHERE CO_ENTIDADE = ?", (CO_ENTIDADE,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"ERROR": "Instituição não encontrada."}), 404

        instituicaoEnsino = InstituicaoEnsino(
            NO_REGIAO=row[0],
            CO_REGIAO=row[1],
            NO_UF=row[2],
            SG_UF=row[3],
            CO_UF=row[4],
            NO_MUNICIPIO=row[5],
            CO_MUNICIPIO=row[6],
            CO_MESORREGIAO=row[7],
            CO_MICRORREGIAO=row[8],
            NO_ENTIDADE=row[9],
            CO_ENTIDADE=row[10],
            QT_MAT_BAS=row[11],
            QT_MAT_EJA=row[12],
            QT_MAT_ESP=row[13],
            QT_MAT_FUND=row[14],
            QT_MAT_INF=row[15],
            QT_MAT_MED=row[16],
            QT_MAT_PROF=row[17],
        )

        return jsonify(instituicaoEnsino.toDict()), 200

    except sqlite3.Error as e:
        logger.exception("Exception sqlite: %s", e)
        return jsonify({"ERROR": "Problema com o banco de dados."}), 500
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
