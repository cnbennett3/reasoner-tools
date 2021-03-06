'''
Set up Flask server
'''

import logging.config
import os
import sys

from flask import Flask, Blueprint
from flask_restful import Api
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__, static_folder='../pack', template_folder='../templates')
# Set default static folder to point to parent static folder where all
# static assets can be stored and linked
# app.config.from_pyfile('robokop_flask_config.py')

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_blueprint)
CORS(app)
app.register_blueprint(api_blueprint)

template = {
    "openapi": "2.0", #3.0.1",
    "info": {
        "title": "Rosetta Workflow API",
        "description": "An API for executing semantic distributed biomedical analytic workflows over semantically harmonized knowledge sources.",
        "contact": {
            "responsibleOrganization": "RENCI",
            "responsibleDeveloper": "scox@renci.org",
            "email": "scox@renci.org",
            "url": "www.renci.org",
        },
        "termsOfService": "<url>",
        "version": "0.0.1"
    },
    "schemes": [
        "http",
        "https"
    ]
}
app.config['SWAGGER'] = {
    'title': 'Roetta Workflow API',
    'uiversion': 3
}
swagger = Swagger(app, template=template)
