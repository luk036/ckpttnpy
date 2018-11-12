import networkx as nx
from collections import deque
from dllist import dllist, dlnode
from bpqueue import bpqueue

G = nx.Graph()
G.add_nodes_from([
    ('a1', {'type': 'cell', 'weight': 58444, 'isfix': True}),
    ('a2', {'type': 'cell', 'weight': 34565, 'ispad': True}),
    ('n1', {'type': 'net', 'weight': 1}),
    ('n2', {'type': 'net', 'weight': 1, 'fixed': True})
])
cell_list = ['a1', 'a2']
cell_dict = {'a1': 0, 'a2': 1}
part = [1, 0]
net_list = ['n1', 'n2']

G.add_edges_from([
    ('a1', 'n1', {'dir': 'in'}),
    ('a1', 'n2', {'dir': 'out'}),
    ('a2', 'n1', {'dir': 'bidir'}),
    ('a2', 'n2', {'dir': 'unknown'})
])

DiG = nx.to_directed(G)

num = [0, 1]


def updateMove2PinNet(net, part, fromPart, v):
    assert G.degree[net] == 2
    netCur = iter(G[net])
    w = next(netCur)
    if w == v:
        w = next(netCur)
    i_w = cell_dict[w]
    part_w = part[i_w]
    weight = G[net].get('weight', 1)
    deltaGainW = 2*weight if (part_w == fromPart) else -2*weight
    return part_w, i_w, deltaGainW


def updateMoveGeneralNet(net, part, fromPart, v):
    # assert G.degree[net] > 2
    IdVec = list()
    deltaGain = list()
    degree = 0
    for w in G[net]:
        if w == v:
            continue
        IdVec.append(cell_dict[w])
        deltaGain.append(0)
        degree += 1

    if degree == 0: # ???
        return

    m = G[net].get('weight', 1)
    weight = m if fromPart == 0 else -m
    for k in [0, 1]:
        if num[k] == 0:
            for idx in range(degree):
                deltaGain[idx] -= weight
        elif num[k] == 1:
            for idx in range(degree):
                part_w = part[IdVec[idx]]
                if part_w == k:
                    deltaGain[idx] += weight
                    break
        weight = -weight


if __name__ == "__main__":
    vertexlist = list(dlnode(i) for i in range(2))
    gainbucket = bpqueue(-10, 10)
    gainbucket.append(vertexlist[1], 6)
    print(gainbucket.get_max())

    gainmax = gainbucket.get_max()
    dlv = gainbucket.popleft()
    v = cell_list[dlv.id]
    print(G.degree[v])
    for n in G[v]:
        print(n)
    res = updateMove2PinNet('n1', part, 1, 'a1')
    print(res)
    updateMoveGeneralNet('n1', part, 1, 'a1')
