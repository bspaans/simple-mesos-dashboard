from hamcrest import *
from dashboard import Node

def test_node_to_dict():
    node = Node(1, "hostname")
    result = node.to_dict()
    assert_that(result["id"], equal_to(1))
    assert_that(result["hostname"], equal_to("hostname"))

def test_node_add_resources():
    node = Node(1, "hostname")
    resources1 = {'mem': 16.0, 'cpus': 4}
    resources2 = {'mem': 10.0, 'cpus': 1}
    node.add_resources('framework_name', resources1)
    node.add_resources('framework_name', resources2)
    result = node.to_dict()
    assert_that(result['mem'], equal_to(26))
    assert_that(result['cpu'], equal_to(5))

def test_node_set_max_resources():
    node = Node(1, "hostname")
    node.set_max_resources(26, 5)
    result = node.to_dict()
    assert_that(result['max_mem'], equal_to(26))
    assert_that(result['max_cpu'], equal_to(5))
