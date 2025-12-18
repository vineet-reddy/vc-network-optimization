
import networkx as nx
import random
import os
from .config import DATA_FILE, SEED

def load_graph():
    """
    Loads the Bitcoin Alpha dataset into an UNDIRECTED NetworkX graph.
    
    Design Decision: Although the raw data contains directed edges (A rated B),
    we convert to undirected because in the VC talent map context, professional
    relationships are inherently mutual - if you know someone, they know you.
    A rating from A to B indicates they have interacted/worked together.
    
    For edges that exist in both directions (A→B and B→A), we average the ratings.
    For edges in only one direction, we use the single rating as the relationship strength.
    
    Assigns:
    - Node 'talent_score': Mean trust rating received (reputation)
    - Edge 'weight': Trust rating (averaged if bidirectional)
    - Node 'last_contacted': Days since most recent interaction
    - Node 'maintenance_cost': Time to reconnect (randomized)
    """
    print(f"Loading graph from {DATA_FILE}...")
    
    # First load into a directed graph to preserve all rating information
    DG = nx.DiGraph()
    
    # 1. Parse Data
    # Format: SOURCE, TARGET, RATING, TIME
    # RATING: -10 to +10
    # TIME: Unix timestamp
    
    try:
        raw_edges = []
        timestamps = []
        
        with open(DATA_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    u = int(parts[0])
                    v = int(parts[1])
                    rating = int(parts[2])
                    timestamp = int(parts[3])
                    
                    raw_edges.append((u, v, rating, timestamp))
                    timestamps.append(timestamp)
                    
                    # Add edge to directed graph first
                    DG.add_edge(u, v, weight=rating, timestamp=timestamp)

    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_FILE}")
        return None

    print(f"Directed graph loaded. Nodes: {DG.number_of_nodes()}, Edges: {DG.number_of_edges()}")
    
    # Convert to UNDIRECTED graph
    # For edge weights: if both A→B and B→A exist, average ratings; else use single rating
    # For timestamps: use the most recent timestamp between the pair
    G = nx.Graph()
    
    # Add all nodes first
    G.add_nodes_from(DG.nodes())
    
    # Process edges - combine bidirectional edges
    processed_pairs = set()
    for u, v, data in DG.edges(data=True):
        # Use sorted tuple to identify unique pairs regardless of direction
        pair = tuple(sorted([u, v]))
        if pair in processed_pairs:
            continue
        processed_pairs.add(pair)
        
        # Check both directions
        weight_uv = DG[u][v]['weight'] if DG.has_edge(u, v) else None
        weight_vu = DG[v][u]['weight'] if DG.has_edge(v, u) else None
        ts_uv = DG[u][v]['timestamp'] if DG.has_edge(u, v) else 0
        ts_vu = DG[v][u]['timestamp'] if DG.has_edge(v, u) else 0
        
        # Combine weights: average if both directions exist
        if weight_uv is not None and weight_vu is not None:
            combined_weight = (weight_uv + weight_vu) / 2
        else:
            combined_weight = weight_uv if weight_uv is not None else weight_vu
        
        # Use most recent timestamp
        combined_timestamp = max(ts_uv, ts_vu)
        
        G.add_edge(pair[0], pair[1], weight=combined_weight, timestamp=combined_timestamp)
    
    print(f"Converted to undirected. Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    if not raw_edges:
        return G

    # 2. Compute Attributes
    random.seed(SEED)
    
    # Calculate "Now" for staleness (Max timestamp in dataset)
    max_time = max(timestamps)
    
    # Pre-calculate incoming ratings for Talent Score
    # Talent Score = Mean Trust Rating Received
    node_ratings = {} # {node_id: [list of ratings received]}
    
    for u, v, rating, time in raw_edges:
        if v not in node_ratings:
            node_ratings[v] = []
        node_ratings[v].append(rating)
        
        # Ensure simple nodes exist even if they have no edges (though they come from edges)
        if not G.has_node(u): G.add_node(u)
        if not G.has_node(v): G.add_node(v)

    # Assign Node Attributes
    for node in G.nodes():
        # A. Talent Score
        ratings = node_ratings.get(node, [])
        if ratings:
            mean_rating = sum(ratings) / len(ratings)
            # Normalize or shift? 
            # Ratings are -10 to +10. 
            # Proposal says "Talent Scores... Mean trust rating".
            # Let's keep it raw for now, or shift to positive if algorithms need it.
            # Greedy/IP maximization usually prefers positive weights.
            # Start with raw, but optimization might fail if weights are negative.
            # Proposal Objective: Maximize sum(w_j * y_j).
            # If w_j is negative, we wouldn't want to pick them.
            # But "Talent" usually implies value. 
            # Let's assume w_j is simply the value.
            score = mean_rating
        else:
            score = 0 # specific neutral value? Or -10? 0 seems safe.
            
        G.nodes[node]['talent_score'] = score
        
        # B. Last Contacted (Staleness)
        # We need 'last_contacted_days_ago' for the Maintenance problem.
        # Find the most recent interaction involving this node (either as source or target? Or just target?)
        # Proposal: "timestamp of the most recent rating involving a contact represents when that relationship was last active"
        # "Involving a contact" could mean Source OR Target.
        # But usually maintenance means "When did *I* last talk to them?"
        # The graph is global. 
        # For the maintenance problem, we are usually optimizing *our* relationships.
        # Let's check the Maintenance problem definition in code or proposal.
        # Proposal: "last engaged... timestamp of the most recent rating involving a contact".
        # We will scan all edges connected to `node` (in or out) to find max timestamp.
        
        node_timestamps = []
        for u, v, w, t in raw_edges:
            if u == node or v == node:
                node_timestamps.append(t)
        
        if node_timestamps:
            last_ts = max(node_timestamps)
            diff_seconds = max_time - last_ts
            days_ago = int(diff_seconds / (3600 * 24))
            # Ensure at least 1 day to avoid div by zero if logic requires
            days_ago = max(1, days_ago)
        else:
            days_ago = 730 # Default old
            
        G.nodes[node]['last_contacted'] = days_ago
        
        # C. Maintenance Cost
        # Random as before
        G.nodes[node]['maintenance_cost'] = random.randint(15, 120)

    return G

if __name__ == "__main__":
    load_graph()
