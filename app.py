from helpers.application import app, api
from helpers.CORS import cors

from resources.InstituicaoResource import InstituicoesResource, InstituicaoResource
from resources.IndexResource import IndexResource

cors.init_app(app)

api.add_resource(IndexResource, '/')
api.add_resource(InstituicoesResource, '/instituicoes')
api.add_resource(InstituicaoResource, '/instituicoes/<int:CO_ENTIDADE>')

if __name__ == "__main__":
    app.run(debug=True)