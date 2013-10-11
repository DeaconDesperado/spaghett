import argparse
import os
from threading import Thread
from Queue import Queue
import re
import networkx as nx
from networkx.readwrite import json_graph

def is_import_line(line):
    return re.match('(?:import)',line)

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

class DependencySpaghetti(object):

    def __init__(self,path,top_package):
        self.q = Queue()
        self.graph = nx.Graph()
        self.top_package = top_package
        for root,dirs,files in os.walk(path):
            for fl in files:
                if fl.endswith('java'):
                    self.q.put('%s/%s' %(root,fl))

    def consume(self):
        while not self.q.empty():
            module = open(self.q.get())
            try:
                this_module = get_module(module)
                if not filter_on_package(self.top_package,this_module):
                    continue
                self.graph.add_node(this_module)
                imports = map(get_package_from_line,  [line for line in module if is_import_line(line) and filter_on_package(self.top_package,line)])
                for impt in imports:
                    if filter_on_package(self.top_package,impt):
                        self.graph.add_node(impt)
                        self.graph.add_edge(this_module,impt)
            except StopIteration:
                print module.name

        dc = nx.degree_centrality(self.graph)
        nx.set_node_attributes(self.graph,'degree_cent',dc)
        return json_graph.dump(self.graph,open('graph.json','w'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('top_package')
    args = parser.parse_args()
    ds = DependencySpaghetti(args.path,args.top_package)
    print ds.consume() 
