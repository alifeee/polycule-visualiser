"""open polycule.json and make necessary edits"""

import json
from edit import (
    Node,
    Edge,
    parse_graph,
    assemble_graph,
    create_node,
    delete_node,
    rename_node,
    create_edge,
    delete_edge,
)

# nodes equate
assert Node("alifeee") == Node("alifeee"), "nodes do not equate"

# edges equate
assert Edge("alifeee", "jman", type_="normal") == Edge(
    "alifeee", "jman", type_="normal"
), "edges do not equate"
assert Edge("alifeee", "jman", type_="normal") == Edge(
    "jman", "alifeee", type_="normal"
), "edges with swapped to/from do not equate"
assert Edge("alifeee", "jman", type_="normal") == Edge(
    "alifeee", "jman", type_="dashed"
), "edges with different types should equate but they do not"

# set up "identical" graphs
graph_json = '{"nodes":[{"name":"alifeee"},{"name":"jman"},{"name":"somebody"},{"name":"Paul"}],"edges":[{"from":"alifeee","to":"jman"},{"from":"alifeee","to":"somebody","type":"dashed"}]}'
original_graph = json.loads(graph_json)

nodes = [Node("jman"), Node("somebody"), Node("alifeee"), Node("Paul")]
edges = [Edge("alifeee", "jman", type_=""), Edge("somebody", "alifeee", type_="dashed")]

# test parse_graph
graph_nodes, graph_edges = parse_graph(original_graph)
assert len(graph_nodes) == len(nodes), "parsed graph lost nodes?"
for node in graph_nodes:
    assert node in nodes, f"node '{node}' not in edges"
assert len(graph_edges) == len(edges), "parsed graph lost edges?"
for edge in graph_edges:
    assert edge in edges, f"edge '{edge}' not in edges"

# test assemble_graph
assert (
    json.dumps(assemble_graph(nodes, edges))
    == '{"nodes": [{"name": "jman"}, {"name": "somebody"}, {"name": "alifeee"}, {"name": "Paul"}], "edges": [{"from": "alifeee", "to": "jman"}, {"from": "somebody", "to": "alifeee", "type": "dashed"}]}'
), "assemble_graph did badly"

# test delete node
errors, graph = delete_node(original_graph, [], "brian")
assert len(errors) == 1, "deleting non-existent node worked when it should have failed"

errors, graph = delete_node(original_graph, [], "alifeee")
assert len(errors) == 1, "deleting node with edge worked when it should have failed"

errors, graph = delete_node(original_graph, [], "Paul")
assert (
    len(errors) == 0 and {"name": "Paul"} not in graph["nodes"]
), "Paul was not deleted"

# test create node
errors, graph = create_node(original_graph, [], "alifeee")
assert len(errors) == 1, "adding already existing node worked. it should not."

errors, graph = create_node(original_graph, [], "ulysees")
assert len(errors) == 0 and {"name": "ulysees"} in graph["nodes"], "adding node failed"

# test delete edge
errors, graph = delete_edge(original_graph, [], ["alifeee", "Paul"])
assert len(errors) == 1, "non-existent edge was not caught"

errors, graph = delete_edge(original_graph, [], ["alifeee", "jman"])
assert (
    len(errors) == 0 and Edge("alifeee", "jman", "") not in parse_graph(graph)[1]
), "failed to delete edge"

# test create edge
errors, graph = create_edge(original_graph, [], ["alifeee", "jman"])
assert len(graph["edges"]) == len(
    original_graph["edges"]
), "create edge did not catch already-existing edge"

errors, graph = create_edge(original_graph, [], ["Marge", "alifeee"])
assert len(errors) > 0, "create_edge did not error for non-existent edge - 1st"

errors, graph = create_edge(original_graph, [], ["alifeee", "Marge"])
assert len(errors) > 0, "create_edge did not error for non-existent edge - 2nd"

errors, graph = create_edge(original_graph, [], ["alifeee", "Paul"])
assert (
    len(errors) == 0 and Edge("alifeee", "Paul", "") in parse_graph(graph)[1]
), "failed to add edge"

errors, graph = create_edge(original_graph, [], ["alifeee", "Paul"], dashed=True)
assert len(errors) == 0 and (
    parse_graph(graph)[1][-1].type_ == "dashed"
), "failed to add edge as dashed"

# test rename node
errors, graph = rename_node(original_graph, [], ["Homer", "Alfie"])
assert len(errors) == 1, "rename_node did not complain about nonexistent node"

errors, graph = rename_node(original_graph, [], ["alifeee", "jman"])
assert len(errors) == 1, "rename_node did not complain about existent renamed node"

errors, graph = rename_node(original_graph, [], ["alifeee", "Alfie"])
assert (
    len(errors) == 0
    and (Node("alifeee") not in parse_graph(graph)[0])
    and (Node("Alfie") in parse_graph(graph)[0])
), "rename_node did not successfully rename node"
assert (Edge("Alfie", "jman", "") in parse_graph(graph)[1]) and (
    Edge("Alfie", "somebody", "") in parse_graph(graph)[1]
), "rename_node did not rename relevant edges"

# test that functions preserve edge types
errors, graph = create_node(original_graph, [], "newnode")
errors, graph = delete_node(graph, [], "newnode")
errors, graph = create_node(graph, [], "newnode")
errors, graph = create_edge(graph, [], ["somebody", "jman"])
errors, graph = delete_edge(graph, [], ["somebody", "jman"])
errors, graph = rename_node(graph, [], ["jman", "jfiddy"])
assert {"from": "alifeee", "to": "somebody", "type": "dashed"} in graph[
    "edges"
], "functions did not preserve edge type"

print("tests passed ok !")
