from flask import request
from flask_restful import Resource, marshal
import psycopg2
from marshmallow import ValidationError
from helpers.database import getConnection
from helpers.logging import logger, log_exception
from models.InstituicaoEnsino import (
    instiuicao_fields,
    InstituicaoEnsino,
    InstituicaoEnsinoSchema,
)

colunas = (
    "nu_ano_censo",
    "no_regiao", "co_regiao", "no_uf", "sg_uf", "co_uf",
    "no_municipio", "co_municipio", "co_mesorregiao", "co_microrregiao",
    "no_entidade", "co_entidade",
    "qt_mat_bas", "qt_mat_eja", "qt_mat_esp", "qt_mat_fund",
    "qt_mat_inf", "qt_mat_med", "qt_mat_prof"
)

SELECT_COLUNAS = ", ".join(colunas)
CHAVE = {nome: i for i, nome in enumerate(colunas)}


class InstituicoesResource(Resource):
    def get(self):
        page = int(request.args.get("page", 10000))
        per_page = int(request.args.get("per_page", 1))
        ano = request.args.get("ano", type=int)
        offset = (page - 1) * per_page
        logger.info(f"GET ALL - page={page} | per_page={per_page} | offset={offset}")
        try:
            conn = getConnection()
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT {SELECT_COLUNAS}
                FROM instituicoes
                ORDER BY nu_ano_censo, co_entidade
                LIMIT %s OFFSET %s
                """,
                (per_page, offset)
            )
            linhas = cur.fetchall()
            instituicoes = []
            for linha in linhas:
                instituicao = InstituicaoEnsino(
                    NU_ANO_CENSO=linha[CHAVE["nu_ano_censo"]],
                    NO_REGIAO=linha[CHAVE["no_regiao"]],
                    CO_REGIAO=linha[CHAVE["co_regiao"]],
                    NO_UF=linha[CHAVE["no_uf"]],
                    SG_UF=linha[CHAVE["sg_uf"]],
                    CO_UF=linha[CHAVE["co_uf"]],
                    NO_MUNICIPIO=linha[CHAVE["no_municipio"]],
                    CO_MUNICIPIO=linha[CHAVE["co_municipio"]],
                    CO_MESORREGIAO=linha[CHAVE["co_mesorregiao"]],
                    CO_MICRORREGIAO=linha[CHAVE["co_microrregiao"]],
                    NO_ENTIDADE=linha[CHAVE["no_entidade"]],
                    CO_ENTIDADE=linha[CHAVE["co_entidade"]],
                    QT_MAT_BAS=linha[CHAVE["qt_mat_bas"]],
                    QT_MAT_EJA=linha[CHAVE["qt_mat_eja"]],
                    QT_MAT_ESP=linha[CHAVE["qt_mat_esp"]],
                    QT_MAT_FUND=linha[CHAVE["qt_mat_fund"]],
                    QT_MAT_INF=linha[CHAVE["qt_mat_inf"]],
                    QT_MAT_MED=linha[CHAVE["qt_mat_med"]],
                    QT_MAT_PROF=linha[CHAVE["qt_mat_prof"]],
                )
                instituicoes.append(instituicao)
            logger.info("Instituições retornadas com sucesso!")
            return marshal(instituicoes, instiuicao_fields), 200

        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def post(self):
        schema = InstituicaoEnsinoSchema()
        dados = request.get_json()
        logger.info("POST - Instituição")
        try:
            inst = schema.load(dados)

            conn = getConnection()
            cur = conn.cursor()

            cur.execute(
                f"""
                INSERT INTO instituicoes
                ({SELECT_COLUNAS})
                VALUES (
                    %s,%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s
                )
                ON CONFLICT (co_entidade, nu_ano_censo) DO UPDATE
                SET no_regiao = EXCLUDED.no_regiao,
                    co_regiao = EXCLUDED.co_regiao,
                    no_uf = EXCLUDED.no_uf,
                    sg_uf = EXCLUDED.sg_uf,
                    co_uf = EXCLUDED.co_uf,
                    no_municipio = EXCLUDED.no_municipio,
                    co_municipio = EXCLUDED.co_municipio,
                    co_mesorregiao = EXCLUDED.co_mesorregiao,
                    co_microrregiao = EXCLUDED.co_microrregiao,
                    no_entidade = EXCLUDED.no_entidade,
                    qt_mat_bas = EXCLUDED.qt_mat_bas,
                    qt_mat_eja = EXCLUDED.qt_mat_eja,
                    qt_mat_esp = EXCLUDED.qt_mat_esp,
                    qt_mat_fund = EXCLUDED.qt_mat_fund,
                    qt_mat_inf = EXCLUDED.qt_mat_inf,
                    qt_mat_med = EXCLUDED.qt_mat_med,
                    qt_mat_prof = EXCLUDED.qt_mat_prof
                """,
                (
                    inst["NU_ANO_CENSO"],
                    inst["NO_REGIAO"], inst["CO_REGIAO"], inst["NO_UF"], inst["SG_UF"], inst["CO_UF"],
                    inst["NO_MUNICIPIO"], inst["CO_MUNICIPIO"], inst["CO_MESORREGIAO"], inst["CO_MICRORREGIAO"],
                    inst["NO_ENTIDADE"], inst["CO_ENTIDADE"],
                    inst.get("QT_MAT_BAS"), inst.get("QT_MAT_EJA"), inst.get("QT_MAT_ESP"), inst.get("QT_MAT_FUND"),
                    inst.get("QT_MAT_INF"), inst.get("QT_MAT_MED"), inst.get("QT_MAT_PROF"),
                )
            )
            conn.commit()

            instituicaoEnsino = InstituicaoEnsino(
                NU_ANO_CENSO=inst["NU_ANO_CENSO"],
                NO_REGIAO=inst["NO_REGIAO"],
                CO_REGIAO=inst["CO_REGIAO"],
                NO_UF=inst["NO_UF"],
                SG_UF=inst["SG_UF"],
                CO_UF=inst["CO_UF"],
                NO_MUNICIPIO=inst["NO_MUNICIPIO"],
                CO_MUNICIPIO=inst["CO_MUNICIPIO"],
                CO_MESORREGIAO=inst["CO_MESORREGIAO"],
                CO_MICRORREGIAO=inst["CO_MICRORREGIAO"],
                NO_ENTIDADE=inst["NO_ENTIDADE"],
                CO_ENTIDADE=inst["CO_ENTIDADE"],
                QT_MAT_BAS=inst.get("QT_MAT_BAS"),
                QT_MAT_EJA=inst.get("QT_MAT_EJA"),
                QT_MAT_ESP=inst.get("QT_MAT_ESP"),
                QT_MAT_FUND=inst.get("QT_MAT_FUND"),
                QT_MAT_INF=inst.get("QT_MAT_INF"),
                QT_MAT_MED=inst.get("QT_MAT_MED"),
                QT_MAT_PROF=inst.get("QT_MAT_PROF"),
            )

            logger.info(
                f"Instituição (CO_ENTIDADE={inst['CO_ENTIDADE']}, ANO={inst['NU_ANO_CENSO']}) criada com sucesso!"
            )
            return marshal(instituicaoEnsino, instiuicao_fields), 201

        except ValidationError as err:
            logger.warning(f"Erro(s) de validação: {err.messages}")
            return {"ERROR": "Falha na validação dos dados.", "detalhes": err.messages}, 422
        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                cur.close()
            except Exception:
                pass


class InstituicaoResource(Resource):
    def get(self, CO_ENTIDADE, NU_ANO_CENSO):
        logger.info(f"GET BY CO_ENTIDADE & ANO- Instituição ({CO_ENTIDADE}, {NU_ANO_CENSO})")
        try:
            conn = getConnection()
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT {SELECT_COLUNAS}
                FROM instituicoes
                WHERE co_entidade = %s AND nu_ano_censo = %s
                """,
                (CO_ENTIDADE, NU_ANO_CENSO)
            )
            row = cur.fetchone()
            if row is None:
                return {"ERROR": "Instituição não encontrada."}, 404

            inst = InstituicaoEnsino(
                NU_ANO_CENSO=row[CHAVE["nu_ano_censo"]],
                NO_REGIAO=row[CHAVE["no_regiao"]],
                CO_REGIAO=row[CHAVE["co_regiao"]],
                NO_UF=row[CHAVE["no_uf"]],
                SG_UF=row[CHAVE["sg_uf"]],
                CO_UF=row[CHAVE["co_uf"]],
                NO_MUNICIPIO=row[CHAVE["no_municipio"]],
                CO_MUNICIPIO=row[CHAVE["co_municipio"]],
                CO_MESORREGIAO=row[CHAVE["co_mesorregiao"]],
                CO_MICRORREGIAO=row[CHAVE["co_microrregiao"]],
                NO_ENTIDADE=row[CHAVE["no_entidade"]],
                CO_ENTIDADE=row[CHAVE["co_entidade"]],
                QT_MAT_BAS=row[CHAVE["qt_mat_bas"]],
                QT_MAT_EJA=row[CHAVE["qt_mat_eja"]],
                QT_MAT_ESP=row[CHAVE["qt_mat_esp"]],
                QT_MAT_FUND=row[CHAVE["qt_mat_fund"]],
                QT_MAT_INF=row[CHAVE["qt_mat_inf"]],
                QT_MAT_MED=row[CHAVE["qt_mat_med"]],
                QT_MAT_PROF=row[CHAVE["qt_mat_prof"]],
            )
            return marshal(inst, instiuicao_fields), 200

        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def put(self, CO_ENTIDADE, NU_ANO_CENSO):
        logger.info(f"PUT - Instituição ({CO_ENTIDADE}, {NU_ANO_CENSO})")
        try:
            conn = getConnection()
            cur = conn.cursor()

            cur.execute(
                "SELECT 1 FROM instituicoes WHERE co_entidade = %s AND nu_ano_censo = %s",
                (CO_ENTIDADE, NU_ANO_CENSO)
            )
            if cur.fetchone() is None:
                return {"ERROR": "Instituição não encontrada."}, 404

            schema = InstituicaoEnsinoSchema()
            dados = schema.load(request.get_json())

            cur.execute(
                """
                UPDATE instituicoes
                SET no_regiao=%s, co_regiao=%s, no_uf=%s, sg_uf=%s, co_uf=%s,
                    no_municipio=%s, co_municipio=%s, co_mesorregiao=%s, co_microrregiao=%s,
                    no_entidade=%s, qt_mat_bas=%s, qt_mat_eja=%s, qt_mat_esp=%s,
                    qt_mat_fund=%s, qt_mat_inf=%s, qt_mat_med=%s, qt_mat_prof=%s
                WHERE co_entidade=%s AND nu_ano_censo=%s
                """,
                (
                    dados["NO_REGIAO"], dados["CO_REGIAO"], dados["NO_UF"], dados["SG_UF"], dados["CO_UF"],
                    dados["NO_MUNICIPIO"], dados["CO_MUNICIPIO"], dados["CO_MESORREGIAO"], dados["CO_MICRORREGIAO"],
                    dados["NO_ENTIDADE"], dados.get("QT_MAT_BAS"), dados.get("QT_MAT_EJA"), dados.get("QT_MAT_ESP"),
                    dados.get("QT_MAT_FUND"), dados.get("QT_MAT_INF"), dados.get("QT_MAT_MED"), dados.get("QT_MAT_PROF"),
                    CO_ENTIDADE, NU_ANO_CENSO
                )
            )
            conn.commit()

            return {"MENSAGEM": "Instituição atualizada com sucesso."}, 200

        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {"ERROR": "Falha na validação dos dados.", "detalhes": err.messages}, 422
        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def delete(self, CO_ENTIDADE, NU_ANO_CENSO):
        logger.info(f"DELETE - Instituição ({CO_ENTIDADE}, {NU_ANO_CENSO})")
        try:
            conn = getConnection()
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM instituicoes WHERE co_entidade = %s AND nu_ano_censo = %s",
                (CO_ENTIDADE, NU_ANO_CENSO)
            )
            conn.commit()

            if cur.rowcount == 0:
                return {"ERROR": "Instituição não encontrada."}, 404

            return {"MENSAGEM": "Instituição removida com sucesso."}, 200

        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500
        finally:
            try:
                cur.close()
            except Exception:
                pass


class InstituicaoAnoResource(Resource):
    def get(self, NU_ANO_CENSO):
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)
        offset = (page - 1) * per_page
        logger.info(f"GET - Ano: {NU_ANO_CENSO} | page={page} | per_page={per_page} | offset={offset}")
        try:
            conn = getConnection()
            cur = conn.cursor()

            cur.execute(
                f"""
                    SELECT {SELECT_COLUNAS}
                    FROM instituicoes
                    WHERE nu_ano_censo = %s
                    ORDER BY co_entidade
                    LIMIT %s OFFSET %s
                """,
                (NU_ANO_CENSO, per_page, offset)
            )
            rows = cur.fetchall()

            if not rows:
                return {"ERROR": "Nenhuma instituição encontrada para este ano."}, 404

            instituicoes = []
            for row in rows:
                inst = InstituicaoEnsino(
                    NU_ANO_CENSO=row[CHAVE["nu_ano_censo"]],
                    NO_REGIAO=row[CHAVE["no_regiao"]],
                    CO_REGIAO=row[CHAVE["co_regiao"]],
                    NO_UF=row[CHAVE["no_uf"]],
                    SG_UF=row[CHAVE["sg_uf"]],
                    CO_UF=row[CHAVE["co_uf"]],
                    NO_MUNICIPIO=row[CHAVE["no_municipio"]],
                    CO_MUNICIPIO=row[CHAVE["co_municipio"]],
                    CO_MESORREGIAO=row[CHAVE["co_mesorregiao"]],
                    CO_MICRORREGIAO=row[CHAVE["co_microrregiao"]],
                    NO_ENTIDADE=row[CHAVE["no_entidade"]],
                    CO_ENTIDADE=row[CHAVE["co_entidade"]],
                    QT_MAT_BAS=row[CHAVE["qt_mat_bas"]],
                    QT_MAT_EJA=row[CHAVE["qt_mat_eja"]],
                    QT_MAT_ESP=row[CHAVE["qt_mat_esp"]],
                    QT_MAT_FUND=row[CHAVE["qt_mat_fund"]],
                    QT_MAT_INF=row[CHAVE["qt_mat_inf"]],
                    QT_MAT_MED=row[CHAVE["qt_mat_med"]],
                    QT_MAT_PROF=row[CHAVE["qt_mat_prof"]],
                )
                instituicoes.append(marshal(inst, instiuicao_fields))

            return instituicoes, 200

        except psycopg2.Error:
            log_exception("Exception psycopg2")
            return {"ERROR": "Problema com o banco de dados."}, 500

        finally:
            try:
                cur.close()
            except Exception:
                pass

class MatriculasPorEstadoResource(Resource):
    def get(self):
        ano = request.args.get("ano", type=int)
        logger.info(f"PARA API")
        if ano is None:
            return {"ERROR": "Parâmetro 'ano' é obrigatório."}, 400
        
        try:
            conn = getConnection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT sg_uf, SUM(COALESCE(qt_mat_bas, 0) + COALESCE(qt_mat_eja, 0) +
                                 COALESCE(qt_mat_esp, 0) + COALESCE(qt_mat_fund, 0) +
                                 COALESCE(qt_mat_inf, 0) + COALESCE(qt_mat_med, 0) +
                                 COALESCE(qt_mat_prof, 0)) AS total_matriculas
                FROM instituicoes
                WHERE nu_ano_censo = %s
                GROUP BY sg_uf
                ORDER BY sg_uf
                """,
                (ano,)
            )
            resultados = cur.fetchall()
            resposta = {uf: total for uf, total in resultados}
            return resposta, 200
        except Exception:
            log_exception("Erro ao buscar matrículas por estado")
            return {"ERROR": "Erro interno no servidor."}, 500
        finally:
            try:
                cur.close()
            except:
                pass