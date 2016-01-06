#!/usr/bin/env python 

import os 
import requests
import json
import sys
from flask import Flask
from flask.ext.restful import Api, Resource

MESOS=os.environ.get('MESOS', None)
TEST_MODE = False

class Node(object):
    def __init__(self, node_id, hostname):
        self.node_id = node_id
        self.hostname = hostname
        self.resources = []
        self.cpu_total = 0.0
        self.mem_total = 0.0
        self.max_mem   = 0.0
        self.max_cpu   = 0.0
        self.tasks     = []

    def add_resources(self, framework_name, cpu, mem):
        self.cpu_total += cpu 
        self.mem_total += mem 
        self.resources.append((framework_name, cpu, mem))

    def set_max_resources(self, max_mem, max_cpu):
        self.max_mem = max_mem
        self.max_cpu = max_cpu

    def add_task(self, task):
        self.tasks.append(task)
        if task.is_running():
            self.add_resources(task.framework.name, task.cpu, task.mem)

    def _tasks_to_dict(self):
        result = {}
        for t in self.tasks:
            task_dict = t.to_dict()
            result[task_dict["id"]] = task_dict
        return result

    def to_dict(self):
        return {'id': self.node_id, 'hostname': self.hostname,
            'mem': self.mem_total, 'cpu': self.cpu_total,
            'max_cpu': self.max_cpu, 'max_mem': self.max_mem,
            'tasks': self._tasks_to_dict()}

class Nodes(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def get_by_id(self, node_id):
        if node_id not in self.nodes:
            return None
        return self.nodes[node_id]

    def to_dict(self):
        result = {}
        for n in self.nodes.itervalues():
            node_dict = n.to_dict()
            result[node_dict["id"]] = node_dict
        return result

class Framework(object):
    def __init__(self, framework_id, name, hostname, active):
        self.framework_id = framework_id
        self.name = name
        self.hostname = hostname
        self.active = active
        self.tasks = {}
        self.completed_tasks = {}

    def set_completed_tasks(self, tasks):
        self.completed_tasks = tasks

    def set_tasks(self, tasks):
        self.tasks = tasks

    def to_dict(self):
        return {"id": self.framework_id,
                "name": self.name,
                "hostname": self.hostname,
                "active": self.active,
                "tasks": map(lambda t: t.task_id, self.tasks.values())
		}

class Task(object):
    def __init__(self, framework, task_id, name, state):
        self.framework = framework
        self.task_id = task_id
        self.name = name
        self.cpu = 0.0
        self.mem = 0.0
        self.disk = 0.0
        self.node = None
        self.state = state

    def is_running(self):
        return self.state == "TASK_RUNNING"

    def set_resources(self, cpu, mem, disk):
        self.cpu = cpu
        self.mem = mem
        self.disk = disk

    def set_node(self, node):
        self.node = node

    def to_dict(self):
        return {"framework_id": self.framework.framework_id,
                "name": self.name,
                "id": self.task_id,
                "cpu": self.cpu,
                "mem": self.mem,
                "disk": self.disk,
                "node_id": self.node.node_id,
                "state": self.state}

class MesosResponseParser(object):
    def __init__(self):
        self.nodes = None
        self.frameworks = {}

    def parse(self, json_payload):
        self.nodes = self._parse_nodes(json_payload['slaves'])
        self.frameworks = self._parse_frameworks(json_payload['frameworks'])

    def _parse_nodes(self, nodes):
        result = {}
        for slave in nodes:
            node_id = slave['id']
            node = result.get(node_id, Node(node_id, slave['hostname']))
            node.set_max_resources(slave['resources']['mem'], slave['resources']['cpus'])
            result[node_id] = node
        return Nodes(result)

    def _parse_frameworks(self, frameworks):
        result = {}
        for framework in frameworks:
            framework_id = framework["id"]
            name = framework["name"]
            hostname = framework["hostname"]
            active = framework["active"]
            f = Framework(framework_id, name, hostname, active)
            f.set_tasks(self._parse_tasks(f, framework["tasks"]))
            f.set_completed_tasks(self._parse_tasks(f, framework["completed_tasks"]))
            result[framework_id] = f
        return result

    def _parse_tasks(self, framework, tasks):
        result = {}
        for task in tasks:
            task_id = task["id"]
            name = task["name"]
            status = task["state"]
            t = Task(framework, task_id, name, status)

            cpu = task["resources"]["cpus"]
            mem = task["resources"]["mem"]
            disk = task["resources"]["disk"]
            t.set_resources(cpu, mem, disk)

            slave_id = task["slave_id"]
            node = self.nodes.get_by_id(slave_id)
            if node is not None:
                node.add_task(t)
                t.set_node(node)
            result[task_id] = t
        return result

class NodeStatisticsResource(Resource):
    def _mesos_endpoint(self, mesos_host = None):
        if mesos_host is None:
            mesos_host = MESOS
        return mesos_host + "/state.json"

    def _get_master_from_payload(self, payload, key):
        if key not in payload:
            return None
        master = payload[key]
        return "http://" + master[len("master@"):]

    def get(self):
        if not TEST_MODE:
            payload = requests.get(self._mesos_endpoint()).text
        else: 
            with open("tests/test_response.json") as f:
                payload = f.read()
        json_payload = json.loads(payload)
        master = self._get_master_from_payload(json_payload, "master")
        if master is None:
            master = self._get_master_from_payload(json_payload, "leader")
        if master is None:
            return 503
        if master != MESOS and not TEST_MODE:
            payload = requests.get(self._mesos_endpoint(master)).text
            json_payload = json.loads(payload)
        parser = MesosResponseParser()
        parser.parse(json_payload)
        node_breakdown = parser.nodes.to_dict()
        frameworks = {}
        for id_, f in parser.frameworks.iteritems():
            frameworks[id_] = f.to_dict()
	
        taskToNodes = {}
        for n in parser.nodes.nodes.itervalues():
            for t in n.tasks:
                taskToNodes[t.task_id] = n.node_id;
        return {"nodes": node_breakdown, "master": master, "frameworks": frameworks, "tasks": taskToNodes}

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
    if MESOS is None:
        if "--test-mode" in sys.argv:
            TEST_MODE = True
        else:
            raise Exception("Missing MESOS environment variable and not in --test-mode")
    app.run(host='0.0.0.0', debug=True)
