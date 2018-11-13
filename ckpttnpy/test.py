import networkx as nx
from collections import deque
from dllist import dllink
from bpqueue import bpqueue

G = nx.Graph()
G.add_nodes_from([
    ('a1', {'type': 'cell', 'weight': 58444, 'fixed': True}),
    ('a2', {'type': 'cell', 'weight': 34565, 'ispad': True}),
    ('a3', {'type': 'cell', 'weight': 345}),
    ('n1', {'type': 'net', 'weight': 1}),
    ('n2', {'type': 'net', 'weight': 1, 'fixed': True})
])
cell_list = ['a1', 'a2', 'a3']
cell_dict = {'a1': 0, 'a2': 1, 'a3': 2}
cell_fixed = {'a1'}
cell_weight = [533, 343, 32]
cell_part = [1, 0, 0]
net_list = ['n1', 'n2']
net_weight = [1, 1]

G.add_edges_from([
    ('a1', 'n1', {'dir': 'in'}),
    ('a1', 'n2', {'dir': 'out'}),
    ('a2', 'n1', {'dir': 'bidir'}),
    ('a2', 'n2', {'dir': 'unknown'}),
    ('a3', 'n2', {'dir': 'unknown'})
])

G = nx.to_directed(G)

num = [0, 1]
net_degree = []

vertexlist = [dllink(i) for i in range(3)]
gainbucket = bpqueue(-10, 10)
gainbucket.append(vertexlist[0], 6)
gainbucket.append(vertexlist[1], 7)
gainbucket.append(vertexlist[2], 8)

def initialization():
    for net in net_list:
        degree = 0
        for w in G[net]:
            if w in cell_fixed:
                continue
            degree += 1
        net_degree.append(degree)



def init2PinNet(net, part):
    assert G.out_degree[net] == 2
    netCur = iter(G[net])
    w = next(netCur)
    v = next(netCur)
    i_w = cell_dict[w]
    i_v = cell_dict[v]
    part_w = part[i_w]
    part_v = part[i_v]
    weight = G[net].get('weight', 1)
    g = -weight if part_w == part_v else weight
    vertexlist[i_w].key += g
    vertexlist[i_v].key += g


def updateMove2PinNet(net, part, fromPart, v):
    assert G.out_degree[net] == 2
    netCur = iter(G[net])
    w = next(netCur)
    if w == v:
        w = next(netCur)
    if w in cell_fixed:
        return
    i_w = cell_dict[w]
    part_w = part[i_w]
    weight = G[net].get('weight', 1)
    deltaGainW = 2*weight if part_w == fromPart else -2*weight
    gainbucket.modify_key(vertexlist[i_w], deltaGainW)


def updateMoveGeneralNet(net, part, fromPart, v):
    assert G.out_degree[net] > 2

    IdVec = []
    deltaGain = []
    degree = 0
    for w in G[net]:
        if w == v:
            continue
        if w in cell_fixed:
            continue
        IdVec.append(cell_dict[w])
        deltaGain.append(0)
        degree += 1

    if degree == 0:
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

    for idx in range(degree):
        gainbucket.modify_key(vertexlist[IdVec[idx]], deltaGain[idx])


if __name__ == "__main__":
    print(gainbucket.get_max())
    gainmax = gainbucket.get_max()
    dlv = gainbucket.popleft()
    v = cell_list[dlv.id]
    print(G.degree[v])
    for n in G[v]:
        print(n)
    initialization()
    init2PinNet('n1', cell_part)
    updateMove2PinNet('n1', cell_part, 1, 'a2')
    updateMoveGeneralNet('n2', cell_part, 1, 'a2')
