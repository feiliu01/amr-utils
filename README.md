amr-utils
=========

A collection of convenience functions for handling AMR (Abstract Meaning Representation) graphs.


	1. A converter from an AMR graph to a list of nodes and edges
===============================================================

Input: an AMR graph
-------------------

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


Output: a list of nodes and edges
---------------------------------

Nodes:

	0 s schedule-01
	0.0 p project
	0.0.0 m monetary-quantity
	0.0.0.0 d dollar
	0.1 c complete-01
	0.2 d2 date-entity

Edges:
	
	s (ARG1)-> p
	p (mod)-> m
	m (unit)-> d
	s (ARG2)-> c
	c (ARG1)-> p
	s (ARG3)-> d2


Usage: 
------

	g = AmrGraph()
	tokens = graph_string.split()
	
	nodes = g.getNodes(tokens)
	edges = g.getEdges(tokens)
	
	for node in nodes: print node
	for edge in edges: print edge
	


