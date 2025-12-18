
import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import math

def calculate_urgency(time_since_contact):
    """
    Calculates the 'Staleness' Value V(t) based on the proposal.
    V(t) = Logarithmic decay urgency.
    Proposal says: "concave function like log(t_i)"
    """
    return math.log(time_since_contact + 1)

def solve_maintenance_ip(G, time_budget, min_staleness=30):
    """
    Solves the Maintenance Problem (Knapsack) using Gurobi.
    
    Per the proposal: "prioritize reconnecting with contacts who provide access to 
    high-density talent clusters and have been inactive the longest."
    
    Value = urgency(staleness) * network_value
    Where network_value considers BOTH talent_score AND connectivity (degree).
    
    The graph is UNDIRECTED - relationships are mutual. A contact who knows many 
    people (high degree) is more valuable to reconnect with than someone who knows 
    few people, all else being equal.
    
    Args:
        G: NetworkX graph (undirected)
        time_budget: Total time available (T)
        
    Returns:
        tuple: (selected_nodes, total_value_recovered)
    """
    print(f"Solving Maintenance IP with Budget T={time_budget}...")
    
    # Filter candidates: "Dormant" relationships
    candidates = []
    
    attrs = G.nodes(data=True)
    
    for n, data in attrs:
        t_i = data.get('last_contacted', 0)
        c_i = data.get('maintenance_cost', 0)
        
        if t_i > min_staleness:
            # Value calculation per proposal:
            # "contacts who provide access to high-density talent clusters"
            # This means we should consider:
            # 1. Staleness (urgency to reconnect)
            # 2. Talent score (quality of the person)
            # 3. Degree (how many mutual connections they have)
            
            urgency = calculate_urgency(t_i)
            talent_score = data.get('talent_score', 0)
            
            # Degree = number of mutual connections (undirected graph)
            degree = G.degree(n)
            
            # Only consider people who actually have connections (degree > 0)
            # and have positive reputation (talent_score > 0)
            if degree > 0 and talent_score > 0:
                # Network value = talent_score * sqrt(degree)
                # Using sqrt to avoid over-weighting extremely high-degree nodes
                network_value = talent_score * math.sqrt(degree)
                value = urgency * network_value
                
                candidates.append({
                    'id': n,
                    'weight': c_i,
                    'value': value,
                    'days_dormant': t_i,
                    'degree': degree,  # Mutual connections
                    'talent_score': talent_score
                })
            
    print(f"Found {len(candidates)} dormant candidates for maintenance.")
    
    model = gp.Model("Maintenance_Knapsack")
    model.Params.OutputFlag = 0
    
    # x[i]: 1 if we reconnect with candidate i
    x = model.addVars(len(candidates), vtype=GRB.BINARY, name="x")
    
    # Objective: Maximize total value
    model.setObjective(gp.quicksum(candidates[i]['value'] * x[i] for i in range(len(candidates))), GRB.MAXIMIZE)
    
    # Constraint: Time Budget
    model.addConstr(gp.quicksum(candidates[i]['weight'] * x[i] for i in range(len(candidates))) <= time_budget, "TimeBudget")
    
    model.optimize()
    
    selected_nodes = []
    recovered_value = 0.0
    
    if model.status == GRB.OPTIMAL:
        for i in range(len(candidates)):
            if x[i].X > 0.5:
                # Add metadata for frontend
                node_info = candidates[i]
                selected_nodes.append(node_info)
                recovered_value += node_info['value']
                
    return selected_nodes, recovered_value
