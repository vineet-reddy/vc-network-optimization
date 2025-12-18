
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import time

def solve_sentinel_ip(G, k):
    """
    Solves the Sentinel Problem (Maximum Coverage) using Gurobi Integer Programming.
    
    The graph is UNDIRECTED - relationships are mutual. If A knows B, then B knows A.
    A Sentinel "covers" all their neighbors (people they have a relationship with).
    
    Args:
        G: NetworkX graph (undirected)
        k: Number of sentinels to select
        
    Returns:
        tuple: (selected_sentinels_list, total_covered_weight, runtime)
    """
    print(f"Solving Sentinel IP with K={k}...")
    start_time = time.time()
    
    # In undirected graph: candidates = anyone with at least one connection
    # talents = anyone who could be covered (also anyone with connections)
    candidates = [n for n in G.nodes() if G.degree(n) > 0]
    talents = [n for n in G.nodes() if G.degree(n) > 0]
    candidates_set = set(candidates)
    
    model = gp.Model("Sentinel_MaxCoverage")
    model.Params.OutputFlag = 0  # Silence output for cleanliness
    model.Params.TimeLimit = 600 # 10 minute timeout safety
    
    # Decision variables
    # x[i]: 1 if candidate i is selected as Sentinel
    x = model.addVars(candidates, vtype=GRB.BINARY, name="x")
    
    # y[j]: 1 if talent j is covered
    y = model.addVars(talents, vtype=GRB.BINARY, name="y")
    
    # Objective: Maximize total weight of covered talent
    # Weight w_j is 'talent_score'
    weights = nx.get_node_attributes(G, 'talent_score')
    model.setObjective(gp.quicksum(weights[j] * y[j] for j in talents), GRB.MAXIMIZE)
    
    # Constraints
    
    # 1. Budget Constraint: Sum x_i <= K
    model.addConstr(gp.quicksum(x[i] for i in candidates) <= k, "Budget")
    
    # 2. Coverage Constraint: y_j <= Sum(x_i for i who know j)
    # In undirected graph, "who knows j" = neighbors of j
    for j in talents:
        # Get list of candidates who know talent j (neighbors in undirected graph)
        knowers = [i for i in G.neighbors(j) if i in candidates_set]
        
        if not knowers:
            # If no one knows this talent (in the candidate set), y[j] must be 0
            model.addConstr(y[j] == 0)
        else:
            model.addConstr(y[j] <= gp.quicksum(x[i] for i in knowers), f"Cover_{j}")
            
    # Optimize
    model.optimize()
    
    runtime = time.time() - start_time
    
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        selected_sentinels = [i for i in candidates if x[i].X > 0.5]
        covered_weight = model.ObjVal
        return selected_sentinels, covered_weight, runtime
    else:
        print("Model failed to converge.")
        return [], 0.0, runtime

def solve_sentinel_greedy(G, k):
    """
    Solves the Sentinel Problem using the Greedy Algorithm (Submodular Maximization).
    
    The graph is UNDIRECTED - relationships are mutual. A Sentinel covers all neighbors.
    
    Args:
        G: NetworkX graph (undirected)
        k: Number of sentinels to select
        
    Returns:
        tuple: (selected_sentinels_list, total_covered_weight, runtime)
    """
    print(f"Solving Sentinel Greedy with K={k}...")
    start_time = time.time()
    
    selected_sentinels = set()
    covered_talent = set()
    current_score = 0.0
    
    # Pre-compute weights and neighborhoods for efficiency
    weights = nx.get_node_attributes(G, 'talent_score')
    
    # In undirected graph: candidates = anyone with at least one connection
    candidates = [n for n in G.nodes() if G.degree(n) > 0]
    
    # Neighbors map: node -> set of people they know (undirected = mutual)
    neighbors_map = {node: set(G.neighbors(node)) for node in candidates}
    
    for _ in range(k):
        best_candidate = None
        best_marginal_gain = -1.0
        
        for candidate in candidates:
            if candidate in selected_sentinels:
                continue
                
            # Calculate marginal gain
            # Gain = Weight of (Neighbors(candidate) - AlreadyCovered)
            new_talents = neighbors_map[candidate] - covered_talent
            gain = sum(weights.get(t, 0) for t in new_talents)
            
            if gain > best_marginal_gain:
                best_marginal_gain = gain
                best_candidate = candidate
        
        if best_candidate is not None and best_marginal_gain > 0:
            selected_sentinels.add(best_candidate)
            covered_talent.update(neighbors_map[best_candidate])
            current_score += best_marginal_gain
            print(f"  Greedy selected {best_candidate} (Gain: {best_marginal_gain:.2f})")
        else:
            break
            
    runtime = time.time() - start_time
    return list(selected_sentinels), current_score, runtime
