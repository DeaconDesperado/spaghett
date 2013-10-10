import argparse
import os
from threading import Thread
from Queue import Queue
import re
import networkx as nx
from networkx.readwrite import json_graph

graph = nx.Graph()

def producer(q,path):
    for root,dirs,files in os.walk(path):
        for fl in files:
            if fl.endswith('java'):
                q.put('%s/%s' %(root,fl))


def is_import_line(line):
    return (re.match('(?:import)',line) and filter_on_package('com.nytimes',line))

def get_package_from_line(line):
    return re.sub('(import|;|\s)','',line)

def get_module(fl):
    name = os.path.basename(fl.name)[:-5]
    package = False
    while not package:
        try:
            ln = fl.next()
            package = re.match('(?:package) [a-zA-Z0-9\.]+',ln).group()
        except AttributeError:
            pass
        
    return '%s.%s' % (re.sub('(package|\;|\s)','',package),name)


def filter_on_package(criteria,it):
    return re.search(criteria,it)

def consumer(q):
    while not q.empty():
        module = open(q.get())
        try:
            this_module = get_module(module)
            if not filter_on_package('com.nytimes',this_module):
                continue
            graph.add_node(this_module)
            imports = map(get_package_from_line,filter(is_import_line,module))
            for impt in imports:
                if filter_on_package('com.nytimes',impt):
                    graph.add_node(impt)
                    graph.add_edge(this_module,impt)
        except StopIteration:
            print module.name

    dc = nx.degree_centrality(graph)
    nx.set_node_attributes(graph,'degree_cent',dc)
    print json_graph.dump(graph,open('graph.json','w'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    args = parser.parse_args()
    q = Queue()
    producer(q,args.path)
    consumer(q)
