#!/usr/bin/env python 

import os 
import requests
import json
from flask import Flask
from flask.ext.restful import Api, Resource

MESOS=os.environ.get('MESOS', None)

class Node(object):
    def __init__(self, node_id):
        self.node_id = node_id
        self.resources = []
        self.cpu_total = 0.0
        self.mem_total = 0.0

    def add_resources(self, framework_name, resources):
        mem = resources.get('mem', 0.0)
        cpu = resources.get('cpus', 0.0)
        self.cpu_total += cpu 
        self.mem_total += mem 
        self.resources.append((framework_name, cpu, mem))

    def to_dict(self):
        return {'id': self.node_id, 'mem': self.mem_total, 'cpu': self.cpu_total}

class NodeStatisticsResource(Resource):
    def mesos_endpoint(self):
        return MESOS + "/state.json"

    def process_frameworks(self, frameworks):
        nodes = {}
        for framework in frameworks:
            name = framework['name']
            for task in framework['tasks']:
                node_id = task['slave_id']
                node = nodes.get(node_id, Node(node_id))
                node.add_resources(name, task['resources'])
                nodes[node_id] = node
        return map(lambda n: n.to_dict(), nodes.values())

    def get(self):
        payload = requests.get(self.mesos_endpoint()).text
        json_payload = json.loads(payload)
        return self.process_frameworks(json_payload['frameworks'])


app = Flask(__name__)
api = Api(app)
api.add_resource(NodeStatisticsResource, '/api/nodes/stats')
if __name__ == '__main__':
    app.run(debug=True)
