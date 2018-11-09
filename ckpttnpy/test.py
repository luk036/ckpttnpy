import networkx as nx
from collections import deque

G = nx.Graph()
G.add_nodes_from([
    ('a1', {'type': 'cell', 'weight' : 58444, 'isfix' : True}),
    ('a2', {'type': 'cell', 'weight' : 34565, 'ispad' : True}),
    ('n1', {'type': 'net'}),
    ('n2', {'type': 'net', 'fixed' : True})
])
cell_list = ['a1', 'a2']
net_list = ['n1', 'n2']

G.add_edges_from([
    ('a1', 'n1', {'dir' : 'in'}),
    ('a1', 'n2', {'dir' : 'out'}),
    ('a2', 'n1', {'dir' : 'bidir'}),
    ('a2', 'n2', {'dir' : 'unknown'})
])

DiG = nx.to_directed(G)
H = dict()
print(H == {})
gainbucket = list(deque() for _ in range(5))
bucket = deque(cell_list)
gainbucket[0] = bucket
gainbucket.append(deque())
gainbucket[4].append('a4')
bucket.append('a3')
bucket.remove(cell_list[0])
print(bucket.popleft())
print(gainbucket)
