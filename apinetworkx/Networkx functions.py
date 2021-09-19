import numpy as np
import scipy as sp
import scipy.sparse.linalg
import requests as req , re , pandas as pd
from pyvis.network import Network
import networkx as nx
from matplotlib import pyplot as plt
import networkx.algorithms.community as nx_comm
 

def create_nx_graph(edge_df):
  fig, ax = plt.subplots(figsize=(18,11))
  G = nx.from_pandas_edgelist(edge_df, 'source', 'target')
  nx.draw(G,with_labels = False, width = edge_df['edge_size'])
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

def degree(G):
  return pd.DataFrame(G.degree(), columns = ["Node", "Degree"])

def modularity(G):
  return nx_comm.modularity(G, nx_comm.label_propagation_communities(G))

#channel_name = input("Enter the channel name: ")
#iterations_number = int(input("Enter the number of iterations: "))
#df = loop(finals(channel_name) , 0 , channel_name, iterations_number)
#create_graph(iterations_number , channel_name)
G = create_nx_graph(df)
hits = df_out_of_nx_hits(G)
degree = degree(G)
modularity = modularity(G)
