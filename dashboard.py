#!/usr/bin/env python 

from flask import Flask
from flask.ext.restful import Api, Resource

class NodeStatisticsResource(Resource):
    def get(self):
        return "alright?"


app = Flask(__name__)
api = Api(app)

api.add_resource(NodeStatisticsResource, '/api/nodes/stats')


if __name__ == '__main__':
    app.run(debug=True)
