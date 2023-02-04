import json
from pprint import pprint, pformat

from typing import List, Callable, Tuple, Union, Optional

class Node:

    def __init__(self, id: str, type: str, **kwargs):
        self.id = id
        self.type = type
        self.subtype = kwargs.get('resource_type', kwargs.get('identity_type', None))

    def __str__(self):
        return f'{self.id.split(":")[-1].split("/")[-1]}'

    def __repr__(self):
        return f'{self.subtype}_{self.type}({self.id.split(":")[-1].split("/")[-1]})'
    
    def __eq__(self, otherNode):
        return self.id == otherNode.id and self.type == otherNode.type
    
class Edge:
 
    def __init__(self, from_: Node, to: Node, type: str):
        self.from_ = from_
        self.to = to
        self.type = type

    def __str__(self):
        return f'{self.from_}----{self.type.replace("roles/","")}----{self.to}'
    
    def __repr__(self):
        return f'{repr(self.from_)}----{self.type.replace("roles/","")}----{repr(self.to)}'

    
    def __eq__(self, otherEdge):
        return self._from == otherEdge._from  and self._to == otherEdge._to and self._type == otherEdge.type

class Graph:

    def __init__(self):
        self._nodes = []
        self._edges = []

    def get_or_insert_node(self, node: Node) -> Node:
        graph_node = self.get_node(node)
        if graph_node is None:
            self._nodes.append(node)
            return node
        graph_node.subtype = node.subtype if graph_node.subtype is None else graph_node.subtype
        return graph_node


    def get_node(self, node: Node) -> Union[Node, None] :
        for graph_node in self._nodes:
            if graph_node == node:
                return graph_node
        return None

    def insert_edge(self, from_: Node, to: Node, type: str) -> Edge:
        edge = Edge(from_, to, type)
        self._edges.append(edge)
        return edge

    def get_edges_by_from_node(self, from_: Node, edge_type: Optional[str] = None) -> List[Edge]:
        if edge_type is None:
            edges_from_node = [ edge for edge in self._edges if edge.from_ == from_ ]
        else:
            edges_from_node = [ edge for edge in self._edges if edge.from_ == from_ and edge.type == edge_type ]
        return edges_from_node
    
    def get_edges_by_to_node(self, to: Node, edge_type: Optional[str] = None) -> List[Edge]:
        if edge_type is None:
            edges_to_node = [ edge for edge in self._edges if edge.to == to ]
        else:
            edges_to_node = [ edge for edge in self._edges if edge.to == to and edge.type == edge_type]
        return edges_to_node
    
    
    def traverse(self, current_node: Node, direction: Optional[str] ='down', recursive: Optional[bool] = True, function: Optional[Callable] = None, output: Optional[List] = []) -> List:
        if direction not in ['up' , 'down'] :
            raise Exception('direction must be "up" or "down"')

        edges = self.get_edges_by_from_node(current_node) if direction == 'down' else self.get_edges_by_to_node(current_node)
        for edge in edges:
            node = edge.to if direction == 'down' else edge.from_
            # do something with the node using function
            # for future
            if recursive:
                self.trav(node , direction, recursive, output)
        return output

    def get_ancestors(self, current_node: Node, ancestors: List = [], edge_type: Optional[str] = None) -> List[str]:
        edges = self.get_edges_by_to_node(current_node, edge_type)
        for edge in edges:
            node = edge.from_
            ancestors.append(str(node))
            self.get_ancestors(node, ancestors, edge_type)
        return ancestors
    
    def get_resource_ancestors(self, current_node: Node) -> List[str]:
        return self.get_ancestors(current_node, ancestors=[], edge_type = 'is_parent_resource_of')
    
    
    def get_resources_and_permissions_of_identity_node(self, current_node: Node, resources_permissions: Optional[List] = [], identity_role: Optional[str] = '') -> List[Tuple[str,str,str]]:
        edges = self.get_edges_by_from_node(current_node)
        for edge in edges:
            node = edge.to
            identity_role = identity_role if edge.type == 'is_parent_resource_of' else edge.type
            #only insert if the node if the edge type is not identity-identity
            if edge.type != 'belongs_to':
                resources_permissions.append((str(node),node.subtype, identity_role.split('/')[-1][:-3]))

            self.get_resources_and_permissions_of_identity_node(node , resources_permissions, identity_role)

        return resources_permissions
    
    def get_identities_and_permissions_of_resource_node(self, current_node: Node, identities_permissions: Optional[List] = [], identity_role: Optional[str] ='') -> List[Tuple[str,str]]:
        edges = self.get_edges_by_to_node(current_node)
        for edge in edges:
            node = edge.from_
            if edge.type != 'is_parent_resource_of':
                identity_role = identity_role if edge.type == 'belongs_to' else edge.type
                identities_permissions.append((str(node), identity_role.split('/')[-1][:-3]))
            self.get_identities_and_permissions_of_resource_node(node , identities_permissions, identity_role=identity_role)
        
        return identities_permissions

    def show(self) -> None:
        print(self)

    def __str__(self) -> str:
        nodes = pformat(self._nodes)
        edges = pformat(self._edges)
        return f"Nodes:\n{nodes}\n\nEdges:\n{edges}"
    
    def get_stat(self) -> str:
        return f'Number of Nodes: {len(self._nodes)}\n Number of Edges: {len(self._edges)}'
        
        