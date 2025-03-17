#!/bin/python3
"""open polycule.json and make necessary edits
you can use this as a file with CLI arguments, try:
  python3 edit.py --help
or it can be a CGI script, test this locally with
  echo "addnode=alifeee" | ./edit.py -cgi
"""

import json
import sys
import os
import argparse
from dataclasses import dataclass
from typing import List, Tuple
from urllib.parse import parse_qsl

FILE = "polycule.json"
DEBUG = True


@dataclass
class Node:
    name: str


@dataclass
class Edge:
    from_: str
    to: str

    def __eq__(self, other):
        if isinstance(other, Edge):
            return (self.from_ == other.from_ and self.to == other.to) or (
                self.from_ == other.to and self.to == other.from_
            )
        return False


@dataclass
class RequestData:
    dry_run: str
    create_node: str
    delete_node: str
    delete_edge: Tuple[str]
    create_edge: Tuple[str]


def debug(msg):
    if DEBUG is True:
        print(msg, file=sys.stderr)


def cgi_error(error: str):
    """return error"""
    print("Content-type: text/plain")
    print()
    print(error)


def parse_graph(graph) -> Tuple[List[Node], List[Edge]]:
    nodes = [Node(n["name"]) for n in graph["nodes"]]
    edges = [Edge(n["from"], n["to"]) for n in graph["edges"]]
    return nodes, edges


def assemble_graph(nodes: List[Node], edges: List[Edge]) -> object:
    return {
        "nodes": [{"name": n.name} for n in nodes],
        "edges": [{"from": e.from_, "to": e.to} for e in edges],
    }


def delete_node(graph, errors, node_todel):
    nodes, edges = parse_graph(graph)

    debug("DELETE NODE")
    debug(
        f" asked to delete {node_todel} from list of {len(nodes)} nodes and {len(edges)} edges"
    )

    # edge case checks
    if node_todel is None:
        return errors, graph
    if node_todel in set().union(set(e.to for e in edges), set(e.from_ for e in edges)):
        errors.append(
            "DELETE NODE: "
            f"must delete all edges connected to {node_todel} before deleting {node_todel}"
        )
        return errors, graph
    if node_todel not in [n.name for n in nodes]:
        errors.append("DELETE NODE: " f"node {node_todel} did not exist to delete it")

    # deletion by filtering
    nodes = [n for n in nodes if n.name != node_todel]

    debug(f" returning graph with {len(nodes)} nodes and {len(edges)} edges")
    return errors, assemble_graph(nodes, edges)


def create_node(graph, errors, node_toadd):
    nodes, edges = parse_graph(graph)

    debug("CREATE NODE")
    debug(
        f" asked to add {node_toadd} to list of {len(nodes)} nodes and {len(edges)} edges"
    )

    # edge case checks
    if node_toadd is None:
        return errors, graph
    if node_toadd in [n.name for n in nodes]:
        errors.append(
            "ADD NODE: " f"cannot add node {node_toadd} as it looks to already exist"
        )
        return errors, graph

    # add node
    nodes.append(Node(node_toadd))

    debug(f" returning graph with {len(nodes)} nodes and {len(edges)} edges")
    return errors, assemble_graph(nodes, edges)


def delete_edge(graph, errors, edge_todel):
    nodes, edges = parse_graph(graph)

    debug("DELETE EDGE")
    debug(
        f" asked to delete {edge_todel} from list of {len(nodes)} nodes and {len(edges)} edges"
    )

    # edge case checks
    if edge_todel is None:
        return errors, graph
    edge = Edge(*edge_todel)
    if edge not in edges:
        errors.append(
            "DELETE EDGE: " f"could not delete {edge_todel} as it did not exist"
        )
        return errors, graph

    edges = [e for e in edges if e != Edge(*edge_todel)]

    debug(f" returning graph with {len(nodes)} nodes and {len(edges)} edges")
    return errors, assemble_graph(nodes, edges)


def create_edge(graph, errors, edge_toadd):
    nodes, edges = parse_graph(graph)

    debug(f"CREATE EDGE")
    debug(
        f" asked to add {edge_toadd} to list of {len(nodes)} nodes and {len(edges)} edges"
    )

    # edge case checks
    if edge_toadd is None:
        return errors, graph
    edge = Edge(*edge_toadd)
    if edge in edges:
        errors.append("ADD EDGE: " f"edge {edge_toadd} was already in edges")
        return errors, graph

    edges.append(edge)

    debug(f" returning graph with {len(nodes)} nodes and {len(edges)} edges")
    return errors, assemble_graph(nodes, edges)


def main(args):
    """do main stuff"""

    debug(f"reading from file {FILE}")
    with open(FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    debug(f"started with {data}")

    # debug objects
    nodes = data["nodes"]
    edges = data["edges"]
    node_ids = [n["name"] for n in nodes]

    errors = []
    # delete
    errors, data = delete_edge(data, errors, args.delete_edge)
    errors, data = delete_node(data, errors, args.delete_node)
    # create
    errors, data = create_node(data, errors, args.create_node)
    errors, data = create_edge(data, errors, args.create_edge)

    if len(errors) > 0:
        print("Content-type: text/plain")
        print()
        print("Errors encountered trying to edit graph:")
        for e in errors:
            print(e)
        return

    debug(f"ended with {data}")

    if args.dry_run:
        debug("dry run complete! quitting now")
        return
    debug(f"writing to file {FILE}")
    with open(FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=" ")

    print("HTTP/1.1 303 See Other")
    print("Location: /polycule/")
    print()
    print("you should be redirected to /polycule/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-nd", "--delete-node", type=str)
    parser.add_argument("-nc", "-na", "--create-node", type=str)
    parser.add_argument("-ed", "--delete-edge", type=str, nargs=2)
    parser.add_argument("-ec", "-ea", "--create-edge", type=str, nargs=2)
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="do not save final JSON, just show output",
    )
    parser.add_argument(
        "-cgi",
        action="store_true",
        help="pretend I'm a CGI request, i.e., take arguments from stdin not from CLI",
    )
    args = parser.parse_args()

    req_method = os.environ.get("REQUEST_METHOD", None)
    # looks like a CGI request
    if req_method == "POST" or args.cgi is True:
        debug("looks like a cgi request! resetting args and reading from stdin...")
        query = dict(parse_qsl(sys.stdin.read()))
        debug(f"got args: {query}")

        addedge1 = query.get("addedge1", None)
        addedge2 = query.get("addedge2", None)
        dcedge1 = query.get("dcedge1", None)
        dcedge2 = query.get("dcedge2", None)

        args = RequestData(
            dry_run=query.get("dry-run", None),
            create_node=query.get("addnode", None),
            delete_node=query.get("removenode", None),
            create_edge=(
                [addedge1, addedge2] if None not in [addedge1, addedge2] else None
            ),
            delete_edge=[dcedge1, dcedge2] if None not in [dcedge1, dcedge2] else None,
        )

    main(args)
