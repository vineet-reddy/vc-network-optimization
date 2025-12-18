#!/usr/bin/env python3
"""
update_paper.py

Updates docs/finalreport.tex with latest results from results/summary.json
"""

import json
import re
import os

def update_paper():
    # Load results
    summary_path = os.path.join('results', 'summary.json')
    tex_path = os.path.join('docs', 'finalreport.tex')
    
    if not os.path.exists(summary_path):
        print(f"Error: {summary_path} not found. Run 'python run_pipeline.py' first.")
        return False
    
    with open(summary_path, 'r') as f:
        data = json.load(f)
    
    with open(tex_path, 'r') as f:
        tex = f.read()
    
    s = data['sentinel_problem']
    m = data['maintenance_problem']
    
    # Update Sentinel Results Table
    # Format: IP (Optimal) & 2417.56 & 0.121 & 100.0\% \\
    tex = re.sub(
        r'IP \(Optimal\) & [\d.]+',
        f"IP (Optimal) & {s['ip_coverage']}",
        tex
    )
    tex = re.sub(
        r'IP \(Optimal\) & [\d.]+ & [\d.]+',
        f"IP (Optimal) & {s['ip_coverage']} & {s['ip_runtime_sec']}",
        tex
    )
    
    tex = re.sub(
        r'Greedy & [\d.]+ & [\d.]+ & [\d.]+',
        f"Greedy & {s['greedy_coverage']} & {s['greedy_runtime_sec']} & {s['greedy_vs_optimal_pct']}",
        tex
    )
    
    tex = re.sub(
        r'Naive \(Top Degree\) & [\d.]+ & [\d.]+ & [\d.]+',
        f"Naive (Top Degree) & {s['naive_coverage']} & {s['naive_runtime_sec']} & {s['naive_vs_optimal_pct']}",
        tex
    )
    
    # Update prose percentages
    tex = re.sub(
        r'achieves [\d.]+% higher coverage',
        f"achieves {s['ip_improvement_over_naive_pct']}% higher coverage",
        tex
    )
    tex = re.sub(
        r'achieves [\d.]+% of optimal coverage',
        f"achieves {s['greedy_vs_optimal_pct']}% of optimal coverage",
        tex
    )
    tex = re.sub(
        r'running [\d.]+x faster',
        f"running {int(s['greedy_speedup_factor'])}x faster",
        tex
    )
    
    # Update Maintenance Results Table
    tex = re.sub(
        r'Time Budget & [\d]+ minutes',
        f"Time Budget & {m['budget_t']} minutes",
        tex
    )
    tex = re.sub(
        r'Relationships Selected & [\d]+',
        f"Relationships Selected & {m['num_selected']}",
        tex
    )
    tex = re.sub(
        r'Total Maintenance Value & [\d.]+',
        f"Total Maintenance Value & {m['total_value']}",
        tex
    )
    tex = re.sub(
        r'Average Dormancy & [\d]+ days',
        f"Average Dormancy & {int(m['avg_days_dormant'])} days",
        tex
    )
    
    # Update prose for maintenance
    tex = re.sub(
        r'selected [\d]+ high-priority relationships',
        f"selected {m['num_selected']} high-priority relationships",
        tex
    )
    tex = re.sub(
        r'average dormancy of [\d]+ days',
        f"average dormancy of {int(m['avg_days_dormant'])} days",
        tex
    )
    
    # Update config values mentioned
    tex = re.sub(
        r'\$K=[\d]+\$ Sentinels',
        f"$K={s['budget_k']}$ Sentinels",
        tex
    )
    tex = re.sub(
        r'\$T=[\d]+\$ minutes',
        f"$T={m['budget_t']}$ minutes",
        tex
    )
    
    # Write updated file
    with open(tex_path, 'w') as f:
        f.write(tex)
    
    print(f"Updated {tex_path} with latest results:")
    print(f"  Sentinel: IP={s['ip_coverage']}, Greedy={s['greedy_coverage']} ({s['greedy_vs_optimal_pct']}%)")
    print(f"  Maintenance: {m['num_selected']} contacts, avg {int(m['avg_days_dormant'])} days dormant")
    return True

if __name__ == "__main__":
    update_paper()

