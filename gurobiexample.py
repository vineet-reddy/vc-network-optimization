import networkx as nx
import gurobipy as gp
from gurobipy import GRB

B = nx.Graph()

labs = ["L1", "L2", "L3", "L4"]
groups = ["G1", "G2", "G3", "G4"]

edges = [
    ("L1", "G1"), ("L3", "G4"),
    ("L1", "G3"), ("L4", "G3"),
    ("L3", "G1"), ("L4", "G4"),
    ("L3", "G2"), ("L2", "G2")
]

# Build the NetworkX graph structure
B.add_nodes_from(labs, bipartite=0)
B.add_nodes_from(groups, bipartite=1)
B.add_edges_from(edges)

m = gp.Model("Problem 2 Part b")

x = m.addVars(B.edges(), vtype=GRB.BINARY, name="x")

# Objective is to max total number of edges selected
m.setObjective(x.sum(), GRB.MAXIMIZE)

# Constraints
for node in B.nodes():
    incident_vars = []
    
    for neighbor in B.neighbors(node):
        # Check which key exists
        if (node, neighbor) in x:
            incident_vars.append(x[node, neighbor])
        elif (neighbor, node) in x:
            incident_vars.append(x[neighbor, node])
            
    m.addConstr(gp.quicksum(incident_vars) <= 1, name=f"limit_{node}")

m.optimize()

if m.status == GRB.OPTIMAL:
    print(f"\nCheck: {m.objVal}")
    print("Assignments:")
    for u, v in B.edges():
        if x[u, v].x > 0.5:
            print(f" {u} is assigned to {v}")