import heapq
import networkx as nx
def xy_to_node(x,y,cols):
    return y*cols+x
def node_to_xy(node,cols):
    return (node%cols,node//cols)
def neighbors(x,y,width,height,diagonal=False):
    dirs=[(1,0),(-1,0),(0,1),(0,-1)]
    if diagonal:
        dirs+=[(1,1),(-1,-1),(1,-1),(-1,1)]
    for dx,dy in dirs :
        nx,ny=x+dx,y+dy
        if 0<=nx<width and 0<=ny<height:
            yield nx,ny
def reachable_tiles(x,y,points,grid):
    reachable={}
    pq=[(0,x,y)]

    while pq:
        cost,cx,cy=heapq.heappop(pq)

        if cost>points:
            continue

        if (cx,cy) in reachable and cost>=reachable[(cx,cy)]:
            continue

        reachable[(cx,cy)]=cost

        for nx_,ny_ in neighbors(cx,cy,grid.width,grid.height):
            tile_cost=grid.weights[(nx_,ny_)]
            heapq.heappush(pq,(cost+tile_cost,nx_,ny_))
    return reachable

def shortest_path(start,target,graph,grid_width,blocked_positions=(),diagonals=False,diagonal_edges=()):
    G=graph.copy()
    if diagonals:
        G.add_edges_from(diagonal_edges)
    print(G.nodes)
    print(blocked_positions)
    for x,y in blocked_positions:
        try:
            G.remove_node((x,y))
        except nx.NetworkXError:
            pass
    try:
        print(G.nodes)
        print(G)
        path=nx.shortest_path(G,(start[0],start[1]),(target[0],target[1]),weight="weight")
    except nx.NetworkXNoPath:
        return []
    return path[1:]

terrains={"dirt":{"weight":1,"img":""},"mud":{"weight":2,"img":""},"water":{"weight":3,"img":""},"stone":{"weight":float("inf"),"img":""}}
def weight_to_color(weight):
    return {1:(50,180,50),2:(160,120,60),3:(50,100,180),4:(128,128,128)}.get(weight,(100,100,100))
    #return terrains[weight]["weight"] if weight in terrains else ""
def closest_enemy(unit,enemies,grid,units):
    blocked=[(u.x,u.y) for u in units if u is not unit and u not in enemies]
    closest=None
    dist=float("inf")
    for enemy in enemies:
        path=shortest_path(
            unit.tile(),
            enemy.tile(),
            grid.graph,grid.width,
            blocked,
            diagonals=unit.diagonal,
            diagonal_edges=grid.diagonal_edges
        )
        if path and len(path)<dist:
            dist=len(path)
            closest=enemy
    return closest
