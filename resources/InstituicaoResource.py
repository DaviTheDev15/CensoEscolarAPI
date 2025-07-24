from flask import request
from flask_restful import Resource, marshal

import sqlite3
from marshmallow import ValidationError

from helpers.database import getConnection
from helpers.logging import logger, log_exception
from models.InstituicaoEnsino import instiuicao_fields

from models.InstituicaoEnsino import InstituicaoEnsino, InstituicaoEnsinoSchema

class InstituicoesResource(Resource):
    def get(self):
        logger.info("GET - Instituições")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 100))
        try:
            instituicoesEnsino = []
            conn = getConnection()
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            cursor.execute(
                'SELECT * FROM Instituicoes LIMIT ? OFFSET ?', (per_page, offset))
            resultSet = cursor.fetchall()
            for row in resultSet:
                logger.info(row)
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
                    QT_MAT_PROF=row[17]
                )
                instituicoesEnsino.append(instituicaoEnsino)
            logger.info("Instituições retornadas com sucesso!")
            return marshal(instituicoesEnsino, instiuicao_fields), 200
        except sqlite3.Error:
            logger.error("Exception sqlite")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            conn.close()
    

    def post(self):
        logger.info("Post - Instituição")
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
            logger.info(f"A instituição portadora do CÓDIGO {CO_ENTIDADE} foi cadastrada com sucesso!")
            return marshal(instituicaoEnsino, instiuicao_fields), 200
        except ValidationError as err:
            logger.warning(f"Erro(s) na validação ao inserir nova instituição: \n\t{err.messages}")
            return {"ERROR": "Falha na validação dos dados. Verifique os campos e tente novamente.", "detalhes": err.messages}, 422
        except sqlite3.Error:
            log_exception("Exception sqlite")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                conn.close()
            except Exception:
                pass
        


class InstituicaoResource(Resource):
    def get(self, CO_ENTIDADE):
        logger.info(f"Get - Instituição por código de entidade: {CO_ENTIDADE}")
        try:
            conn = getConnection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Instituicoes WHERE CO_ENTIDADE = ?", (CO_ENTIDADE,))
            row = cursor.fetchone()
            if row is None:
                logger.warning(f"Instituição com código {CO_ENTIDADE} não encontrada.")
                return {"ERROR": "Instituição não encontrada."}, 404
            logger.info(row)
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
                QT_MAT_PROF=row[17]
            )
            logger.info(f"Instituição com codigo {CO_ENTIDADE} retornada com sucesso")
            return marshal(instituicaoEnsino, instiuicao_fields), 200
        except sqlite3.Error:
            log_exception("Exception sqlite")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            conn.close()
    
    
    def put(self, CO_ENTIDADE):
        logger.info(f"Put - Tentativa de atualizar instituição com código: {CO_ENTIDADE}")
        try:
            conn = getConnection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM Instituições WHERE CO_ENTIDADE = ?', (CO_ENTIDADE,))
            row = cursor.fetchone()
            if row is None:
                logger.warning(f"Instituição com código {CO_ENTIDADE} não encontrada para atualizar.") 
                return {"ERROR": "Instituição não encontrada."}, 404
            
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
            logger.info(f"Instituição com código {CO_ENTIDADE} atualizada com sucesso.")
            return {"MENSAGEM": "Instituição atualizada com sucesso."}, 200
        except ValidationError as err:
            logger.warning(f"Erro de validação ao atualizar instituição com código: {CO_ENTIDADE}\n\t{err.messages}")
            return {"ERROR": "Falha na validação dos dados. Verifique os campos e tente novamente.", "detalhes": err.messages}, 422
        except sqlite3.Error:
            log_exception("Exception sqlite")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            conn.close()

    def delete(self, CO_ENTIDADE):
        logger.info(f"Delete - Tentativa de deleção da instituição com código: {CO_ENTIDADE}")
        try:
            conn = getConnection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Instituicoes WHERE CO_ENTIDADE = ?', (CO_ENTIDADE,))
            conn.commit()
            if cursor.rowcount == 0:
                logger.warning(f"Instituição com código {CO_ENTIDADE} não encontrada para deleção.") 
                return {"ERROR": "Instituição não encontrada."}, 404
            logger.info(f"Instituição com código {CO_ENTIDADE} removida com sucesso.")
            return {"MENSAGEM": "Instituição removida com sucesso."}, 200
        except sqlite3.Error:
            log_exception("Exception sqlite")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            conn.close()

