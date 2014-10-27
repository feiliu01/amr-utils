#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class AmrNode(object):
    def __init__(self, graph_idx=None, short_hnd=None, concept=None):
        self.graph_idx = graph_idx
        self.short_hnd = short_hnd
        self.concept = concept
        
    def __repr__(self):
        return '%s %s %s' % (self.graph_idx, self.short_hnd, self.concept)


class AmrEdge(object):
    def __init__(self, node1=AmrNode(), node2=AmrNode(), relation=None):
        self.node1 = node1
        self.node2 = node2
        self.relation = relation
        return
    
    def __repr__(self):
        return '%s (%s)-> %s' % (self.node1.short_hnd, self.relation, self.node2.short_hnd)


class AmrGraph(object):
    def __init__(self):
        return
    
    def getNodes(self, tokens):
        """
        Obtains a set of nodes from an AMR graph.
                
        Returns:
            A list of nodes of type AmrNode, each node represents a concept.
            
        """
        nodes, curr_idx = self._getNodesIter(None, tokens[:], 0) # copy tokens
        assert curr_idx == len(tokens)
        return [node for node in self._flatten(nodes)] # flatten arbitrarily nested list
    
    def getEdges(self, tokens):
        """
        Obtains a set of edges from an AMR graph.

        Returns:
            A list of edges of type AmrEdge, each edge connects two concepts.
        """
        # get nodes
        nodes = self.getNodes(tokens)
        
        # index nodes by short_hnd
        node_indices = {}
        for node in nodes:
            short_hnd = node.short_hnd
            node_indices.setdefault(short_hnd, node)
        
        # get edges
        edges, curr_idx = self._getEdgesIter(None, tokens[:], 0, node_indices) # copy tokens
        assert curr_idx == len(tokens)-1 or curr_idx == len(tokens)
        
        # enhance edges with node information
        for edge in edges:
            # process node1, add graph_idx, concept
            curr_short_hnd = edge.node1.short_hnd
            if curr_short_hnd in node_indices:
                node = node_indices[curr_short_hnd]
                edge.node1.graph_idx = node.graph_idx
                edge.node1.concept = node.concept
            
            # process node2, add graph_idx, concept
            curr_short_hnd = edge.node2.graph_idx
            if curr_short_hnd in node_indices:
                node = node_indices[curr_short_hnd]
                edge.node2.graph_idx = node.graph_idx
                edge.node2.concept = node.concept
        
        return edges

    def _flatten(self, curr_list):
        """
        _flatten arbitrarily nested list
        """
        for i in curr_list:
            if isinstance(i, list) or isinstance(i, tuple):
                for j in self._flatten(i):
                    yield j
            else:
                yield i

    def _getNodesIter(self, graph_idx, tokens, curr_idx):
        """
        obtain a set of nodes from an AMR graph.
        each node represents a concept.
        """
        nodes = [] # list of nodes
        
        while curr_idx < len(tokens):
            t = tokens[curr_idx]

            if t.endswith(')'):
                tokens[curr_idx] = t[:-1]
                return (nodes, curr_idx)
            
            elif t.startswith('('):
                curr_node = AmrNode()
                curr_node.short_hnd = t[1:]
                curr_idx += 2
                curr_node.concept = re.sub(r'\)+$', '', tokens[curr_idx])
                curr_graph_idx = str(len(nodes)) if not graph_idx else graph_idx + '.' + str(len(nodes))
                curr_node.graph_idx = curr_graph_idx
                nodes.append([curr_node])
                
                # recursion
                new_nodes, new_idx = self._getNodesIter(curr_graph_idx, tokens, curr_idx)
                if new_nodes: nodes.append(nodes.pop() + new_nodes)
                curr_idx = new_idx
                
            else: 
                curr_idx += 1
        
        return nodes, curr_idx
    
    def _getEdgesIter(self, curr_node, tokens, curr_idx, node_indices):
        """
        obtain a set of edges from an AMR graph.
        each edge connects two concepts.
        """
        edges = [] # list of edges
        
        while curr_idx < len(tokens):
            t = tokens[curr_idx]

            # get current node if not provided
            if not curr_node and t.startswith('('):
                curr_node = AmrNode()
                curr_node.short_hnd = t[1:]
                curr_idx += 2
                    
            elif t.endswith(')'):
                tokens[curr_idx] = t[:-1]
                return (edges, curr_idx)
                
            elif t.startswith(':'):
                curr_edge = AmrEdge()
                curr_edge.node1 = curr_node
                curr_edge.relation = t[1:]
                curr_idx += 1
                
                new_t = re.sub(r'\)+$', '', tokens[curr_idx])
                
                # get second node for current edge
                # second node is a new concept
                if new_t.startswith('('):
                    new_node = AmrNode()
                    new_node.short_hnd = tokens[curr_idx][1:]
                    curr_edge.node2 = new_node
                    edges.append(curr_edge)
                    curr_idx += 2
                    
                    # recursion
                    new_edges, new_idx = self._getEdgesIter(new_node, tokens, curr_idx, node_indices)
                    if new_edges: edges.extend(new_edges)
                    curr_idx = new_idx
                
                # second node refers to an old concept (no recursion)
                elif new_t in node_indices:
                    new_node = node_indices[new_t]
                    curr_edge.node2 = new_node
                    edges.append(curr_edge)
                
            else: 
                curr_idx += 1
        
        return edges, curr_idx

 
if __name__ == '__main__':

    # test case 1
    graph_string = '''
    (r / reopen-01
          :ARG1 (u / university :name (n / name :op1 "Naif" :op2 "Arab" :op3 "Academy" :op4 "for" :op5 "Security" :op6 "Sciences")
                :purpose (o / oppose-01
                      :ARG1 (t / terror))
                :mod (e / ethnic-group :name (n3 / name :op1 "Arab")
                      :mod (p / pan)))
          :time (d / date-entity :year 2002 :month 1 :day 5)
          :frequency (f / first
                :time (s / since
                      :op1 (a3 / attack-01
                            :ARG1 (c / country :name (n2 / name :op1 "US"))
                            :time (d2 / date-entity :year 2001 :month 9)))))
    '''

    # test case 2
    graph_string = '''
    (s / schedule-01
        :ARG1 (p / project
            :mod (m / monetary-quantity
                    :unit (d / dollar)
                    :quant 4600000000))
        :ARG2 (c / complete-01
            :ARG1 p)
        :ARG3 (d2 / date-entity
            :year 2003))
    '''
  
  
    g = AmrGraph()
    tokens = graph_string.split()

    nodes = g.getNodes(tokens)
    edges = g.getEdges(tokens)
    
    print
    for node in nodes: print node
    print
    for edge in edges: print edge


            





    
    