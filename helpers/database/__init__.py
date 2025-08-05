import psycopg2
from flask import g
from helpers.application import app

conn_params = {
    'database': 'instituicoes',
    'user': 'postgres',
    'password': 'Souza30072005',
    'host': 'localhost',
    'port': '5432'
}

def connect_raw():
    return psycopg2.connect(**conn_params)

def getConnection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(**conn_params)
    return db


@app.teardown_appcontext
def closeConnection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()