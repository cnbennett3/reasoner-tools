"""Flask REST API server for RoboQuery service"""

import argparse
import json
import os
import requests
import logging
import time
import jsonpath_rw

from flask import Flask, jsonify, g, Response, request
from flasgger import Swagger
from greent.servicecontext import ServiceContext
from flask import request
from flask_restful import Resource, reqparse
import builder.api.roboquery_definitions
import builder.api.roboquery_logging_config
from builder.api.roboquery_setup import app, api

logger = logging.getLogger("roboquery")

class BuildAndRankOneQuestion(Resource):
    def __init__(self, ranker_answer = {}):
        self.ranker_answer = ranker_answer
        return
        
    def post(self, ranker_answer={}):
        """ 
        Initiate a graph query with ROBOKOP Builder and return a Graph with rankings from ROBOKOP Ranker.
        ---
        tags: [RoboQuery]
        parameters:
          - in: body
            name: ok
            description: A machine-readable question graph, entered here, will build
                onto the Knowledge Graph (KG) and return a portion of that KG with rank values.
            schema:
                $ref: '#/definitions/Question'
            required: true
        responses:
            200:
                description: successful operation
            202:
                description: Building onto KG and Ranking results
            400:
                description: Invalid input value(s)    
        """
        # replace `parameters`` with this when OAS 3.0 is fully supported by Swagger UI
        # https://github.com/swagger-api/swagger-ui/issues/3641
        """
        requestBody:
            description: The machine-readable question graph.
            required: true
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Question'
        """
        # First we queue an update to the Knowledge Graph (KG) using ROBOKOP builder
        logger = logging.getLogger('builder KG update task')
        logger.info("Queueing 'KG update' task...")
        
        builder_query_url = "http://127.0.0.1:6010/api/"
        builder_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        
        robokop_query_data = request.json
        builder_query_response = requests.post(builder_query_url, \
          headers = builder_query_headers, json = robokop_query_data)
        builder_task_id = builder_query_response.json()
        builder_task_id_string = builder_task_id["task id"]

        #now query ROBOKOP Builder for the status of Knowledge Graph work
        logger = logging.getLogger('builder KG update status query')
        logger.info("Checking status of 'KG update' task...")
        
        break_loop = False
        while not break_loop:
          time.sleep(1)
          builder_task_status_url = "http://127.0.0.1:6010/api/task/"+builder_task_id_string
          builder_task_status_response = requests.get(builder_task_status_url)
          builder_status = builder_task_status_response.json()
          if builder_status['status'] == 'SUCCESS':
            break_loop = True
         
        #KG has been updated by Builder, get answers NOW from ROBOKOP Ranker!
        logger = logging.getLogger('Ranker Answer query')
        logger.info("Getting Answers about KG from Ranker...")

        ranker_now_query_url = "http://127.0.0.1:6011/api/now"
        ranker_now_query_headers = {
          'accept' : 'application/json',
          'Content-Type' : 'application/json'
          }
        ranker_now_query_response = requests.post(ranker_now_query_url, \
          headers = builder_query_headers, json = robokop_query_data)
        self.ranker_answer = ranker_now_query_response.json()
        
        return self.ranker_answer        

api.add_resource(BuildAndRankOneQuestion, '/one_question')

if __name__ == '__main__':

    # Get host and port from environmental variables
    server_host = '0.0.0.0' #os.environ['ROBOQUERY_HOST']
    server_port = int(os.environ['ROBOQUERY_PORT'])

    app.run(host=server_host,\
        port=server_port,\
        debug=False,\
        use_reloader=True)