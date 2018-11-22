import networkx as nx
# from collections import deque
from ckpttnpy.dllist import dllink
from ckpttnpy.bpqueue import bpqueue

G = nx.Graph()
G.add_nodes_from([
    (0, {'type': 'cell', 'weight': 5844, 'fixed': True}),
    (1, {'type': 'cell', 'weight': 3456, 'ispad': True}),
    (2, {'type': 'cell', 'weight': 345}),
    (3, {'type': 'net', 'weight': 1}),
    (4, {'type': 'net', 'weight': 1, 'fixed': True})
])
cell_list = [0, 1, 2]
# cell_dict = {0: 0, 1: 1, 2: 2}
cell_fixed = {0}
cell_weight = [533, 343, 32]
cell_part = [1, 0, 0]
net_list = [3, 4]
net_weight = [1, 1]

G.add_edges_from([
    (0, 3, {'dir': 'in'}),
    (0, 4, {'dir': 'out'}),
    (1, 3, {'dir': 'bidir'}),
    (1, 4, {'dir': 'unknown'}),
    (2, 4, {'dir': 'unknown'})
])

num = [0, 1]
net_degree = []
# G = nx.DiGraph(G)

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


def init_2pin_net(net, part):
    assert G.degree[net] == 2
    netCur = iter(G[net])
    w = next(netCur)
    v = next(netCur)
    # i_w = cell_dict[w]
    # i_v = cell_dict[v]
    part_w = part[w]
    part_v = part[v]
    weight = G[net].get('weight', 1)
    g = -weight if part_w == part_v else weight
    vertexlist[w].key += g
    vertexlist[v].key += g


def update_move_2pin_net(net, part, fromPart, v):
    assert G.degree[net] == 2
    netCur = iter(G[net])
    w = next(netCur)
    if w == v:
        w = next(netCur)
    if w in cell_fixed:
        return
    # i_w = cell_dict[w]
    part_w = part[w]
    weight = G[net].get('weight', 1)
    deltaGainW = 2*weight if part_w == fromPart else -2*weight
    gainbucket.modify_key(vertexlist[w], deltaGainW)


def update_move_general_net(net, part, fromPart, v):
    assert G.degree[net] > 2

    IdVec = []
    deltaGain = []
    degree = 0
    for w in G[net]:
        if w == v:
            continue
        if w in cell_fixed:
            continue
        IdVec.append(w)
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


def test_experiment():
    print(gainbucket.get_max())
    # gainmax = gainbucket.get_max()
    dlv = gainbucket.popleft()
    v = cell_list[dlv.idx]
    print(G.degree[v])
    for n in G[v]:
        print(n)
    initialization()
    init_2pin_net(3, cell_part)
    update_move_2pin_net(3, cell_part, 1, 1)
    update_move_general_net(4, cell_part, 1, 1)

if __name__ == "__main__":
    test_experiment()

