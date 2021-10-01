import numpy as np
import scipy as sp
import pandas as pd
from pyvis.network import Network
import networkx as nx
from matplotlib import pyplot as plt
import networkx.algorithms.community as nx_comm
 
 

def getG(edge_df):
  G = nx.from_pandas_edgelist(edge_df, 'source', 'target')
  return(G)

def df_out_of_nx_hits(G):
  hits = nx.hits(G, max_iter = 100)
  hubs = hits[0]
  hubs_node = hubs.keys()
  hubs_values = hubs.values()
  auth = hits[1]
  auth_node = auth.keys()
  auth_values = auth.values()
  hubs_df = pd.DataFrame(
    {'node' : hubs_node,
    'hubs' : hubs_values,
    'auth' : auth_values
    }
    )
  return hubs_df

def get_degree(G):
  return pd.DataFrame(G.degree(), columns = ["Node", "Degree"])

def get_modularity(G):
  return nx_comm.modularity(G, nx_comm.label_propagation_communities(G))

def draw_graph(df):
  G = getG(df)
  hits = df_out_of_nx_hits(G)
  degree = get_degree(G)
  modularity = get_modularity(G)
  nt = Network()
  nt.from_nx(G)
  nt.show('nx.html')

def get_elements(G):
  cytodata = nx.cytoscape_data(G)
  elements = cytodata['elements']
  edges1 = elements['edges']
  pos = nx.layout.spring_layout(G)
  edf = pd.DataFrame.from_dict(pos , orient='index' , columns=['x' , 'y'])
  edf.reset_index(level=0, inplace=True)
  nodes = []
  for index , row in edf.iterrows():
      node = {
          'data':{'id':row['index'] ,'label':row['index']},
          'position':{'x':row['x']*2000 , 'y':row['y']*2000}
          }
      nodes.append(node)
  elements1 = {'nodes':nodes , 'edges':edges1}
  return elements1