#!/usr/bin/env python 

import os 
import requests
import json
from flask import Flask
from flask.ext.restful import Api, Resource

MESOS=os.environ.get('MESOS', None)
if MESOS is None:
    raise Exception("Missing MESOS environment variable")

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

    def set_hostname(self, hostname):
        self.hostname = hostname

    def set_max_resources(self, resources):
        self.max_mem = resources.get('mem', 0.0)
        self.max_cpu = resources.get('cpus', 0.0)

    def to_dict(self):
        return {'id': self.node_id, 'hostname': self.hostname,
            'mem': self.mem_total, 'cpu': self.cpu_total,
            'max_cpu': self.max_cpu, 'max_mem': self.max_mem}

class NodeStatisticsResource(Resource):
    def mesos_endpoint(self, mesos_host = None):
        if mesos_host is None:
            mesos_host = MESOS
        return mesos_host + "/state.json"

    def process_frameworks(self, nodes, frameworks):
        for framework in frameworks:
            name = framework['name']
            for task in framework['tasks']:
                node_id = task['slave_id']
                node = nodes.get(node_id, Node(node_id))
                node.add_resources(name, task['resources'])
                nodes[node_id] = node
        return map(lambda n: n.to_dict(), nodes.values())

    def process_slaves(self, slaves):
        nodes = {}
        for slave in slaves:
            node_id = slave['id']
            node = nodes.get(node_id, Node(node_id))
            node.set_max_resources(slave['resources'])
            node.set_hostname(slave['hostname'])
            nodes[node_id] = node
        return nodes

    def get_master_from_payload(self, payload):
        master = payload["leader"]
        return "http://" + master[len("master@"):]


    def get(self):
        payload = requests.get(self.mesos_endpoint()).text
        json_payload = json.loads(payload)
        master = self.get_master_from_payload(json_payload)
        if master != MESOS:
            payload = requests.get(self.mesos_endpoint(master)).text
            json_payload = json.loads(payload)
        nodes = self.process_slaves(json_payload['slaves'])
        node_breakdown = self.process_frameworks(nodes, json_payload['frameworks'])
        return {"nodes": node_breakdown, "master": master}

app = Flask(__name__)
api = Api(app)
api.add_resource(NodeStatisticsResource, '/api/nodes/stats')


@app.route("/")
def index():
    f = open("static/index.html")
    index = f.read()
    f.close()
    return index, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
