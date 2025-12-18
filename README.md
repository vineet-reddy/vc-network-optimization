# Network Optimization Project

## Overview
This project implements network optimization algorithms to solve strategic relationship building problems in professional networks. It uses the **Bitcoin Alpha** signed trust network to model professional connections, endorsements, and relationship decay.

The system addresses two core problems:
1. **The Sentinel Problem**: Selecting an optimal set of contacts ("Sentinels") to maximize access to unique talent in the network, minimizing redundancy. (Modeled as Maximum Coverage).
2. **The Maintenance Problem**: Prioritizing which dormant relationships to re-engage based on their potential value and staleness. (Modeled as the Knapsack Problem).

## Features
- **Data Modeling**: Parses `soc-sign-bitcoinalpha.csv`, interpreting trust ratings as talent scores and timestamps as last contact times.
- **Optimization Algorithms**:
    - **Integer Programming (Gurobi)**: Solves for the exact optimal set of Sentinels and Maintenance targets.
    - **Greedy Algorithm**: Provides a fast approximation for the Sentinel problem.
    - **Naive Baseline**: Selects highest-degree nodes for comparison.
- **Interactive Visualization**: Next.js web app with force-directed graph visualization.
- **Results Export**: Outputs optimization results and graph visualization data to JSON files.

## Project Structure
```
240-final-project/
├── data/
│   ├── soc-sign-bitcoinalpha.csv  # Bitcoin Alpha Trust Network Dataset
│   └── people-10000.csv           # Synthetic names & contact info
├── frontend/                      # Next.js Web App & Visualization
│   ├── public/data/               # Generated output (JSON) for viz
│   └── src/                       # Frontend source code
├── results/                       # Copy of results for easy access
├── src/
│   ├── config.py                  # Settings & parameters
│   ├── data_loader.py             # Data parsing
│   ├── analysis.py                # Detailed analysis with metadata
│   └── models/
│       ├── sentinel.py            # Max Coverage Implementations
│       └── maintenance.py         # Knapsack Implementation
├── run_pipeline.py                # Full pipeline script
├── update_paper.py                # Updates LaTeX with latest results
├── requirements.txt               # Python dependencies
└── README.md
```

## Prerequisites
- **Python 3.12** with Gurobi Optimizer installed and licensed
- **Node.js & npm** for the frontend

## How to Run

### 1. Setup Python Environment
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Optimization Pipeline
```bash
python run_pipeline.py
```

Or for detailed analysis with people metadata:
```bash
python -m src.analysis
```

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Update Paper with Results
```bash
python update_paper.py
```
This updates `docs/projectproposal.tex` with the latest numbers from `results/summary.json`.

### 5. Deploy to Vercel
```bash
cd frontend
vercel --prod
```

## Configuration
Adjust parameters in `src/config.py`:
- `SENTINEL_BUDGET_K`: Number of sentinels to select (default: 10)
- `MAINTENANCE_BUDGET_T`: Time budget for relationship maintenance (default: 2800 minutes)
