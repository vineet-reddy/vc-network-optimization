import json
import os
import networkx as nx
import pandas as pd
from .config import SENTINEL_BUDGET_K, MAINTENANCE_BUDGET_T, RESULTS_DIR
from .data_loader import load_graph
from .models.sentinel import solve_sentinel_ip, solve_sentinel_greedy
from .models.maintenance import solve_maintenance_ip

def ensure_results_dir():
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

def export_results(filename, data):
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Exported {filename} to {path}")

def main():
    ensure_results_dir()
    
    # 1. Load Data
    G = load_graph()
    if G is None:
        return

    # 2. Sentinel Problem
    print("\n--- Running Sentinel Optimization ---")
    
    # IP
    sentinels_ip, weight_ip, time_ip = solve_sentinel_ip(G, SENTINEL_BUDGET_K)
    print(f"IP Solution: {len(sentinels_ip)} sentinels, Coverage: {weight_ip:.2f}, Time: {time_ip:.4f}s")
    
    # Greedy
    sentinels_greedy, weight_greedy, time_greedy = solve_sentinel_greedy(G, SENTINEL_BUDGET_K)
    print(f"Greedy Solution: {len(sentinels_greedy)} sentinels, Coverage: {weight_greedy:.2f}, Time: {time_greedy:.4f}s")
    
    # Compare
    comparison = {
        'ip': {
            'sentinels': sentinels_ip,
            'coverage': weight_ip,
            'runtime': time_ip
        },
        'greedy': {
            'sentinels': sentinels_greedy,
            'coverage': weight_greedy,
            'runtime': time_greedy
        },
        'approximation_ratio': (weight_greedy / weight_ip) if weight_ip > 0 else 0
    }
    export_results('sentinel_results.json', comparison)
    
    # 3. Maintenance Problem
    print("\n--- Running Maintenance Optimization ---")
    maintenance_nodes, maintenance_value = solve_maintenance_ip(G, MAINTENANCE_BUDGET_T)
    print(f"Maintenance Solution: {len(maintenance_nodes)} nodes selected, Value: {maintenance_value:.2f}")
    
    maintenance_results = {
        'selected_nodes': maintenance_nodes,
        'total_value': maintenance_value,
        'budget_used': sum(n['weight'] for n in maintenance_nodes)
    }
    # Note: This export is overwritten later by the enriched version
    
def load_people_metadata():
    """
    Loads people-10000.csv and returns a dict mapping Index (int) to metadata dict.
    """
    try:
        df = pd.read_csv(os.path.join("data", "people-10000.csv"))
        # Ensure Index is int
        df['Index'] = df['Index'].astype(int)
        
        metadata = {}
        for _, row in df.iterrows():
            idx = row['Index']
            metadata[idx] = {
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'email': row['Email'],
                'phone': row['Phone'],
                'job_title': row['Job Title'],
                'dob': row['Date of birth']
            }
        print(f"Loaded metadata for {len(metadata)} people.")
        return metadata
    except Exception as e:
        print(f"Error loading people metadata: {e}")
        return {}

if __name__ == "__main__":
    ensure_results_dir()
    
    # Load People Metadata
    people_meta = load_people_metadata()

    # 1. Load Data
    G = load_graph()
    if G is None:
        exit(1)
        
    # Enrich Graph with People Data
    print("Enriching graph with people metadata...")
    for n in G.nodes():
        if n in people_meta:
            G.nodes[n].update(people_meta[n])

    # 2. Sentinel Problem
    print("\n--- Running Sentinel Optimization ---")
    
    # IP
    sentinels_ip, weight_ip, time_ip = solve_sentinel_ip(G, SENTINEL_BUDGET_K)
    print(f"IP Solution: {len(sentinels_ip)} sentinels, Coverage: {weight_ip:.2f}, Time: {time_ip:.4f}s")
    
    # Greedy
    # sentinels_greedy, weight_greedy, time_greedy = solve_sentinel_greedy(G, SENTINEL_BUDGET_K)
    # print(f"Greedy Solution: {len(sentinels_greedy)} sentinels, Coverage: {weight_greedy:.2f}, Time: {time_greedy:.4f}s")
    
    # Export Sentinel Results with Metadata
    sentinel_export = []
    for sid in sentinels_ip:
        node_data = G.nodes[sid]
        sentinel_export.append({
            'id': sid,
            'val': node_data.get('talent_score', 0),
            'degree': G.degree(sid),  # Mutual connections (undirected graph)
            'metadata': {
                'name': f"{node_data.get('first_name', 'Unknown')} {node_data.get('last_name', '')}".strip(),
                'email': node_data.get('email', 'N/A'),
                'phone': node_data.get('phone', 'N/A'),
                'job': node_data.get('job_title', 'N/A')
            }
        })
        
    export_results('sentinel_results.json', sentinel_export)
    
    # 3. Maintenance Problem
    print("\n--- Running Maintenance Optimization ---")
    maintenance_nodes_raw, maintenance_value = solve_maintenance_ip(G, MAINTENANCE_BUDGET_T)
    print(f"Maintenance Solution: {len(maintenance_nodes_raw)} nodes selected, Value: {maintenance_value:.2f}")
    
    # Enrich Maintenance Results
    maintenance_export = {
        'total_value': maintenance_value,
        'budget_used': sum(n['weight'] for n in maintenance_nodes_raw),
        'selected_nodes': []
    }
    
    for item in maintenance_nodes_raw:
        nid = item['id']
        node_data = G.nodes[nid]
        item['metadata'] = {
            'name': f"{node_data.get('first_name', 'Unknown')} {node_data.get('last_name', '')}".strip(),
            'email': node_data.get('email', 'N/A'),
            'phone': node_data.get('phone', 'N/A'),
            'job': node_data.get('job_title', 'N/A')
        }
        # Include the actual degree for display (undirected = mutual connections)
        item['degree'] = G.degree(nid)
        maintenance_export['selected_nodes'].append(item)

    export_results('maintenance_results.json', maintenance_export)
    
    # 4. Graph Visualization Export
    print("\n--- Generating Visualization Data ---")
    
    important_nodes = set(sentinels_ip) | {n['id'] for n in maintenance_nodes_raw}
    
    # Add top high-talent nodes for context
    sorted_nodes = sorted(G.nodes(data=True), key=lambda x: x[1].get('talent_score', 0), reverse=True)
    top_talent = {n for n, _ in sorted_nodes[:100]} # Increased context
    important_nodes.update(top_talent)
    
    viz_nodes = set(important_nodes)
    for node in important_nodes:
        # Add neighbors (undirected graph - relationships are mutual)
        neighbors = list(G.neighbors(node))[:10]  # Up to 10 neighbors per important node
        viz_nodes.update(neighbors)
        
    subgraph = G.subgraph(viz_nodes)
    
    viz_data = {
        'nodes': [],
        'links': []
    }
    
    for n in subgraph.nodes():
        node_data = G.nodes[n]
        group = 'default'
        if n in sentinels_ip and n in [x['id'] for x in maintenance_nodes_raw]:
            group = 'sentinel_maintenance'  # Both: key contact that needs attention
        elif n in sentinels_ip:
            group = 'sentinel_ip'
        elif n in [x['id'] for x in maintenance_nodes_raw]:
            group = 'maintenance'
        
        # Calculate degree from SUBGRAPH (what's actually visible in the visualization)
        # This matches what users see on screen (undirected = count edges once)
        visible_degree = subgraph.degree(n)
        
        # Also store full graph degree for reference
        full_degree = G.degree(n)
            
        viz_data['nodes'].append({
            'id': n,
            'val': node_data.get('talent_score', 1), # Trust score for sizing
            'degree': visible_degree, # Connections visible in the visualization
            'full_degree': full_degree, # Total connections in full network
            'group': group,
            'label': f"Node {n}", # ID for technical ref
            'metadata': { # Rich metadata for frontend
                'name': f"{node_data.get('first_name', 'Unknown')} {node_data.get('last_name', '')}".strip(),
                'email': node_data.get('email', 'N/A'),
                'phone': node_data.get('phone', 'N/A'),
                'job': node_data.get('job_title', 'N/A')
            }
        })
        
    for u, v in subgraph.edges():
        viz_data['links'].append({
            'source': u,
            'target': v
        })
        
    print(f"Exporting visualization graph: {len(viz_data['nodes'])} nodes, {len(viz_data['links'])} edges.")
    export_results('graph_viz.json', viz_data)
