#!/usr/bin/env python3
"""
run_pipeline.py

Runs the complete optimization pipeline for the Network Optimization project:
1. Sentinel Problem: IP (optimal), Greedy, and Naive baseline
2. Maintenance Problem: IP (optimal)
3. Exports comprehensive results summary for the report
"""

import json
import os
import time
import networkx as nx

from src.config import SENTINEL_BUDGET_K, MAINTENANCE_BUDGET_T, RESULTS_DIR, BASE_DIR
from src.data_loader import load_graph
from src.models.sentinel import solve_sentinel_ip, solve_sentinel_greedy
from src.models.maintenance import solve_maintenance_ip


def ensure_results_dir():
    """Create results directory if it doesn't exist."""
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)


def export_results(filename, data):
    """Export results to JSON file."""
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Exported {filename}")
    return path


def solve_sentinel_naive(G, k):
    """
    Naive baseline: Select the k highest-degree nodes.
    
    This is the "conventional" strategy of targeting the most connected people.
    We hypothesize this performs worse due to redundancy (high-degree nodes
    often know overlapping sets of people).
    """
    print(f"Solving Sentinel Naive (Top {k} Degree) ...")
    start_time = time.time()
    
    # Get all nodes with their degrees
    degrees = [(n, G.degree(n)) for n in G.nodes() if G.degree(n) > 0]
    
    # Sort by degree descending and take top k
    degrees.sort(key=lambda x: x[1], reverse=True)
    selected = [n for n, d in degrees[:k]]
    
    # Calculate coverage (unique talent discovered)
    weights = nx.get_node_attributes(G, 'talent_score')
    covered = set()
    for sentinel in selected:
        covered.update(G.neighbors(sentinel))
    
    total_weight = sum(weights.get(t, 0) for t in covered)
    runtime = time.time() - start_time
    
    return selected, total_weight, runtime


def run_full_pipeline():
    """Run the complete optimization pipeline and export results."""
    
    ensure_results_dir()
    
    print("=" * 60)
    print("NETWORK OPTIMIZATION PIPELINE")
    print("=" * 60)
    
    # 1. Load Graph
    print("\n[1/4] Loading graph data...")
    G = load_graph()
    if G is None:
        print("ERROR: Failed to load graph")
        return None
    
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    print(f"Graph loaded: {num_nodes} nodes, {num_edges} edges")
    
    # 2. Sentinel Problem - Three approaches
    print("\n[2/4] Running Sentinel Optimization...")
    print("-" * 40)
    
    # IP (Optimal)
    sentinels_ip, coverage_ip, time_ip = solve_sentinel_ip(G, SENTINEL_BUDGET_K)
    print(f"  IP (Optimal):  Coverage = {coverage_ip:.2f}, Time = {time_ip:.4f}s")
    
    # Greedy
    sentinels_greedy, coverage_greedy, time_greedy = solve_sentinel_greedy(G, SENTINEL_BUDGET_K)
    print(f"  Greedy:        Coverage = {coverage_greedy:.2f}, Time = {time_greedy:.4f}s")
    
    # Naive (Baseline)
    sentinels_naive, coverage_naive, time_naive = solve_sentinel_naive(G, SENTINEL_BUDGET_K)
    print(f"  Naive:         Coverage = {coverage_naive:.2f}, Time = {time_naive:.4f}s")
    
    # Calculate comparison metrics
    greedy_vs_optimal = (coverage_greedy / coverage_ip * 100) if coverage_ip > 0 else 0
    naive_vs_optimal = (coverage_naive / coverage_ip * 100) if coverage_ip > 0 else 0
    ip_improvement_over_naive = ((coverage_ip - coverage_naive) / coverage_naive * 100) if coverage_naive > 0 else 0
    speedup_greedy = time_ip / time_greedy if time_greedy > 0 else 0
    
    print(f"\n  Greedy achieves {greedy_vs_optimal:.1f}% of optimal")
    print(f"  Naive achieves {naive_vs_optimal:.1f}% of optimal")
    print(f"  IP improves {ip_improvement_over_naive:.1f}% over naive baseline")
    print(f"  Greedy is {speedup_greedy:.1f}x faster than IP")
    
    # 3. Maintenance Problem
    print("\n[3/4] Running Maintenance Optimization...")
    print("-" * 40)
    
    maintenance_nodes, maintenance_value = solve_maintenance_ip(G, MAINTENANCE_BUDGET_T)
    print(f"  Selected {len(maintenance_nodes)} relationships to maintain")
    print(f"  Total maintenance value: {maintenance_value:.2f}")
    
    # Calculate average dormancy of selected nodes
    avg_dormancy = sum(n['days_dormant'] for n in maintenance_nodes) / len(maintenance_nodes) if maintenance_nodes else 0
    
    # 4. Export Results
    print("\n[4/4] Exporting results...")
    print("-" * 40)
    
    # Sentinel comparison results
    sentinel_results = {
        'ip': {
            'sentinels': sentinels_ip,
            'coverage': coverage_ip,
            'runtime': time_ip
        },
        'greedy': {
            'sentinels': sentinels_greedy,
            'coverage': coverage_greedy,
            'runtime': time_greedy
        },
        'naive': {
            'sentinels': sentinels_naive,
            'coverage': coverage_naive,
            'runtime': time_naive
        },
        'comparison': {
            'greedy_vs_optimal_pct': greedy_vs_optimal,
            'naive_vs_optimal_pct': naive_vs_optimal,
            'ip_improvement_over_naive_pct': ip_improvement_over_naive,
            'greedy_speedup_factor': speedup_greedy
        }
    }
    export_results('sentinel_results.json', sentinel_results)
    
    # Maintenance results
    maintenance_results = {
        'selected_nodes': maintenance_nodes,
        'total_value': maintenance_value,
        'budget_used': sum(n['weight'] for n in maintenance_nodes),
        'num_selected': len(maintenance_nodes),
        'avg_days_dormant': avg_dormancy
    }
    export_results('maintenance_results.json', maintenance_results)
    
    # Summary for report
    summary = {
        'dataset': {
            'name': 'Bitcoin Alpha Trust Network',
            'nodes': num_nodes,
            'edges': num_edges
        },
        'sentinel_problem': {
            'budget_k': SENTINEL_BUDGET_K,
            'ip_coverage': round(coverage_ip, 2),
            'ip_runtime_sec': round(time_ip, 4),
            'greedy_coverage': round(coverage_greedy, 2),
            'greedy_runtime_sec': round(time_greedy, 4),
            'naive_coverage': round(coverage_naive, 2),
            'naive_runtime_sec': round(time_naive, 4),
            'greedy_vs_optimal_pct': round(greedy_vs_optimal, 1),
            'naive_vs_optimal_pct': round(naive_vs_optimal, 1),
            'ip_improvement_over_naive_pct': round(ip_improvement_over_naive, 1),
            'greedy_speedup_factor': round(speedup_greedy, 1)
        },
        'maintenance_problem': {
            'budget_t': MAINTENANCE_BUDGET_T,
            'num_selected': len(maintenance_nodes),
            'total_value': round(maintenance_value, 2),
            'avg_days_dormant': round(avg_dormancy, 0)
        }
    }
    export_results('summary.json', summary)
    
    # Also copy to results/ directory in project root for easy access
    root_results_dir = os.path.join(BASE_DIR, 'results')
    if not os.path.exists(root_results_dir):
        os.makedirs(root_results_dir)
    
    for filename in ['sentinel_results.json', 'maintenance_results.json', 'summary.json']:
        src_path = os.path.join(RESULTS_DIR, filename)
        dst_path = os.path.join(root_results_dir, filename)
        with open(src_path, 'r') as f:
            data = json.load(f)
        with open(dst_path, 'w') as f:
            json.dump(data, f, indent=2)
    print(f"  Also copied results to {root_results_dir}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nDataset: {num_nodes} nodes, {num_edges} edges")
    print(f"\nSentinel Problem (K={SENTINEL_BUDGET_K}):")
    print(f"  IP (Optimal):    {coverage_ip:.2f} talent coverage in {time_ip:.3f}s")
    print(f"  Greedy:          {coverage_greedy:.2f} ({greedy_vs_optimal:.1f}% of optimal) in {time_greedy:.3f}s")
    print(f"  Naive Baseline:  {coverage_naive:.2f} ({naive_vs_optimal:.1f}% of optimal)")
    print(f"  -> IP improves {ip_improvement_over_naive:.1f}% over naive")
    print(f"  -> Greedy is {speedup_greedy:.1f}x faster than IP")
    print(f"\nMaintenance Problem (Budget={MAINTENANCE_BUDGET_T}):")
    print(f"  Selected {len(maintenance_nodes)} relationships")
    print(f"  Total maintenance value: {maintenance_value:.2f}")
    print(f"  Average dormancy: {avg_dormancy:.0f} days")
    
    return summary


if __name__ == "__main__":
    run_full_pipeline()

