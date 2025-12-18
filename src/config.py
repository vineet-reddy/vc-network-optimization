
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'soc-sign-bitcoinalpha.csv')
RESULTS_DIR = os.path.join(BASE_DIR, 'frontend', 'public', 'data') # Results output directory

# Parameters
SENTINEL_BUDGET_K = 10
MAINTENANCE_BUDGET_T = 2800 # Your time budget in minutes (~47 hours) for relationship outreach

# Simulation params
SEED = 42
