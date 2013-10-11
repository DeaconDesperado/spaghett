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
    module = re.sub('(import|;|\s)','',line)
    return '.'.join(module.split('.')[:-1]),module

def get_this_module_info(fl):
    name = os.path.basename(fl.name)[:-5]
    package = False
    while not package:
        try:
            ln = fl.next()
            package = re.match('(?:package) ([a-zA-Z0-9\.]+)',ln).groups()[0]
        except AttributeError:
            pass
        
    return package,'%s.%s' % (re.sub('(package|\;|\s)','',package),name)

class DependencySpaghetti(object):

    def __init__(self,path,top_package,resolution=0):
        self.q = Queue()
        self.graph = nx.Graph()
        self.top_package = top_package
        self.resolution = resolution
        for root,dirs,files in os.walk(path):
            for fl in files:
                if fl.endswith('java'):
                    self.q.put('%s/%s' %(root,fl))

    def consume(self):
        while not self.q.empty():
            module = open(self.q.get())
            try:
                this_module = get_this_module_info(module)
                
                self.graph.add_node(this_module[self.resolution],package=this_module[0])

                imports = map(get_package_from_line,  [line for line in module if is_import_line(line)])
                
                for impt in imports:
                    self.graph.add_node(impt[self.resolution],package=impt[0])
                    self.graph.add_edge(this_module[self.resolution],impt[self.resolution])
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
