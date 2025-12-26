import simpy
import networkx as nx
import random
import time
import json
import os

# New Modular Structure Imports
from core.distsim import System
from utils.data_loader import load_flight_graph
from algorithms.toueg_node import TouegNode
from algorithms.floyd_node import FloydNode
from utils import visualizer

# --- HELPER FUNCTIONS ---

def inject_weights_to_nodes(sys: System, G: nx.Graph) -> None:
    """
    Injects real-world edge weights (distances) from NetworkX graph into the simulation nodes.
    This ensures the simulation operates on real kilometer data.
    """
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 100)
        # Update neighbor weights for both directions (if links exist)
        if u in sys.nodes and v in sys.nodes[u].neighbors:
            sys.nodes[u].neighbors[v]['weight'] = weight
        if v in sys.nodes and u in sys.nodes[v].neighbors:
            sys.nodes[v].neighbors[u]['weight'] = weight
        
        # Initialize distance table for FloydNode (Algorithm 7.4 requirement)
        if hasattr(sys.nodes[u], 'D_u'):
             sys.nodes[u].D_u[v] = weight

def make_graph_sparse(G, keep_prob=0.4):
    """
    Randomly removes edges to create a sparse graph for stress testing.
    Ensures the graph remains (weakly) connected.
    """
    G_sparse = G.copy()
    edges = list(G_sparse.edges())
    # Use a fixed seed for reproducibility during tests, or remove for randomness
    # random.seed(42) 
    for u, v in edges:
        if random.random() > keep_prob:
            try: G_sparse.remove_edge(u, v)
            except: pass
            
    # Keep only the largest connected component to ensure reachability
    if len(G_sparse) > 0:
        largest_cc = max(nx.weakly_connected_components(G_sparse), key=len)
        G_sparse = G_sparse.subgraph(largest_cc).copy()
        # Relabel nodes to 0..N range
        G_sparse = nx.convert_node_labels_to_integers(G_sparse, label_attribute='old_id')
    return G_sparse

def calculate_average_degree(G):
    """Calculates the average degree of the graph."""
    if len(G) == 0: return 0
    return sum(dict(G.degree()).values()) / len(G)

# --- EXPERIMENT RUNNER FUNCTIONS ---

def run_experiment_basic(num_nodes, scenario_name, AlgoClass=TouegNode, is_sparse=False):
    """
    Runs Experiment 1 & 2: Validation and Scale Testing.
    Returns: (duration, msg_count, accuracy, avg_degree)
    """
    algo_name = "Toueg" if AlgoClass == TouegNode else "Floyd"
    print(f"\n{'#'*60}")
    print(f"SCENARIO: {scenario_name} (Nodes: {num_nodes}) - {algo_name}")
    print(f"Type: {'SPARSE' if is_sparse else 'DENSE'} Graph")
    print(f"{'#'*60}")

    G = load_flight_graph(num_nodes=num_nodes)
    if G is None: return 0, 0, 0, 0

    if is_sparse:
        G = make_graph_sparse(G, keep_prob=0.3)
        print(f"-> Graph Sparsified. Nodes: {len(G.nodes)}, Edges: {len(G.edges)}")
    
    avg_deg = calculate_average_degree(G)
    print(f"-> Average Degree: {avg_deg:.2f}")

    # Validation: Compute Ground Truth
    print("-> Computing Ground Truth (NetworkX Floyd-Warshall)...")
    real_paths = {}
    try: 
        real_paths = nx.floyd_warshall(G, weight='weight')
    except: 
        print("-> Validation Skipped (Graph might be disconnected)")

    # Initialize Simulation
    sys = System(AlgoClass, nxGraph=G, roundInterval=None)
    inject_weights_to_nodes(sys, G)
    
    start_time = time.time()
    msg_start = sys.msgManager.totalMessageSent
    sim_time_per_round = max(60, num_nodes * 2) 
    
    nodes = list(G.nodes())
    # Pivot Loop
    for i, pivot in enumerate(nodes):
        if (i+1) % 10 == 0: print(f"   > Processing Pivot {i+1}/{len(nodes)}...", end='\r')
        for nid in sys.nodes:
            sys.nodes[nid].mailbox.put(1)
            sys.nodes[nid].messages.append({'type':'START_ROUND', 'sender':-1, 'pivot': pivot})
        sys.env.run(until=sys.env.now + sim_time_per_round)
        
    duration = time.time() - start_time
    msg_count = sys.msgManager.totalMessageSent - msg_start
    
    # Validation Check
    accuracy = 0
    if real_paths:
        check_node = nodes[0]
        sim_table = sys.nodes[check_node].D_u
        gt_table = real_paths[check_node]
        correct, total = 0, 0
        
        for dest in nodes:
            if dest == check_node: continue
            sim_val = sim_table.get(dest, float('inf'))
            real_val = gt_table.get(dest, float('inf'))
            
            if sim_val == float('inf') and real_val == float('inf'): is_ok = True
            elif abs(sim_val - real_val) < 1.0: is_ok = True
            else: is_ok = False
            
            if is_ok: correct += 1
            total += 1
        accuracy = (correct / total * 100) if total > 0 else 0

    print(f"\n--- METRICS ({scenario_name}) ---")
    print(f"1. Execution Time:     {duration:.4f} sec")
    print(f"2. Total Messages:     {msg_count}")
    print(f"3. Graph Density:      {avg_deg:.2f}")
    print(f"4. Validation Accuracy: {accuracy:.1f}%")
    
    return duration, msg_count, accuracy, avg_deg

def run_simulation(AlgoClass, G, algo_name):
    """
    Runs Experiment 3: Complexity Comparison.
    Returns: (duration, msg_count, total_bits)
    """
    print(f"   -> Running {algo_name}...")
    
    sys = System(AlgoClass, nxGraph=G, roundInterval=None)
    inject_weights_to_nodes(sys, G)
    
    start_time = time.time()
    msg_start = sys.msgManager.totalMessageSent
    
    sim_time_per_round = max(60, len(G.nodes) * 3)
    nodes = list(G.nodes())
    total_pivots = len(nodes)
    
    for i, pivot in enumerate(nodes):
        if (i+1) % 5 == 0: print(f"      Pivot {i+1}/{total_pivots}...", end='\r')
        for nid in sys.nodes:
            sys.nodes[nid].mailbox.put(1)
            sys.nodes[nid].messages.append({'type':'START_ROUND', 'sender':-1, 'pivot': pivot})
        sys.env.run(until=sys.env.now + sim_time_per_round)
        
    print(f"      Pivot {total_pivots}/{total_pivots} Done.")
    
    duration = time.time() - start_time
    msg_count = sys.msgManager.totalMessageSent - msg_start
    total_bits = sum(node.total_bits_sent for node in sys.nodes.values())
    
    return duration, msg_count, total_bits

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # Create results directory if it doesn't exist
    if not os.path.exists("results"):
        os.makedirs("results")

    # Dictionary to store all results for the visualizer
    experiment_results = {
        "exp1_scale": {
            "nodes": [],
            "toueg_messages": [],
            "toueg_time": [],
            "floyd_messages": [],
            "floyd_time": []
        },
        "exp2_connectivity": {
            "dense_10": {},
            "sparse_10": {} 
        },
        "exp3_complexity": {
            "toueg": [],
            "floyd": []
        }
    }

    # --- EXPERIMENT 1: SCALE TEST ---
    print("\n>>> STARTING EXPERIMENT 1: VARYING NODE COUNTS <<<")
    
    for count in [10, 20, 30, 40, 50]: 
        # Run Toueg Algorithm
        dur_t, msgs_t, acc_t, deg_t = run_experiment_basic(num_nodes=count, scenario_name=f"Scale Test {count}", AlgoClass=TouegNode)
        
        # Run Floyd Algorithm
        dur_f, msgs_f, acc_f, deg_f = run_experiment_basic(num_nodes=count, scenario_name=f"Scale Test {count}", AlgoClass=FloydNode)
        
        # Store for Scale Chart
        experiment_results["exp1_scale"]["nodes"].append(count)
        experiment_results["exp1_scale"]["toueg_messages"].append(msgs_t)
        experiment_results["exp1_scale"]["toueg_time"].append(dur_t)
        experiment_results["exp1_scale"]["floyd_messages"].append(msgs_f)
        experiment_results["exp1_scale"]["floyd_time"].append(dur_f)
        
        # Store 10-Node Dense result for Connectivity Chart (Experiment 2 baseline)
        if count == 10:
            experiment_results["exp2_connectivity"]["dense_10"] = {
                "Time": f"{dur_t:.4f}s",
                "Messages": msgs_t,
                "Accuracy": f"{acc_t:.1f}%"
            }

    # --- EXPERIMENT 2: CONNECTIVITY TEST ---
    print("\n>>> STARTING EXPERIMENT 2: CONNECTIVITY (SPARSE VS DENSE) <<<")
    # Running 10-Node Sparse to match the visualizer's requirement (10-node comparison)
    dur, msgs, acc, deg = run_experiment_basic(num_nodes=10, scenario_name="Connectivity Test - SPARSE (10 Nodes)", is_sparse=True)
    
    experiment_results["exp2_connectivity"]["sparse_10"] = {
        "Time": f"{dur:.4f}s",
        "Messages": msgs,
        "Accuracy": f"{acc:.1f}%"
    }

    # --- EXPERIMENT 3: COMPLEXITY COMPARISON ---
    print("\n>>> STARTING EXPERIMENT 3: COMPLEXITY COMPARISON (DENSE GRAPH) <<<")
    print("Scenario: High Connectivity Dense Graph (50 Nodes)")
    
    # MODIFICATION TO CREATE DENSE GRAPH:
    # We don't use the make_graph_sparse function.
    # Load the 50-node graph directly.
    G = load_flight_graph(num_nodes=50) 
    
    print(f"Graph Info: {len(G.nodes)} Nodes, {len(G.edges)} Edges")
    avg_deg = calculate_average_degree(G)
    print(f"Average Degree: {avg_deg:.2f}")

    # Warning section can be removed since dense graphs don't fragment
    
    # 1. Run Toueg
    t_time, t_msg, t_bits = run_simulation(TouegNode, G, "Toueg (Algo 7.5)")
    experiment_results["exp3_complexity"]["toueg"] = [t_time, t_msg, t_bits]
    
    # 2. Run Floyd
    f_time, f_msg, f_bits = run_simulation(FloydNode, G, "Dist. Floyd (Algo 7.4)")
    experiment_results["exp3_complexity"]["floyd"] = [f_time, f_msg, f_bits]
    
    # --- PRINT SUMMARY AND SAVE ---
    print("\n\n" + "="*85)
    print(f"{'METRIC':<25} | {'TOUEG':<20} | {'FLOYD':<20} | {'DIFFERENCE'}")
    print("="*85)
    
    # Print message difference for console visibility
    msg_diff = ((f_msg - t_msg) / f_msg) * 100 if f_msg > 0 else 0
    bit_diff = ((f_bits - t_bits) / f_bits) * 100 if f_bits > 0 else 0
    
    print(f"{'Message Count':<25} | {t_msg:<20} | {f_msg:<20} | {msg_diff:+.1f}% (WIN)")
    print(f"{'Bit Complexity':<25} | {t_bits:<20} | {f_bits:<20} | {bit_diff:+.1f}% (WIN)")
        
    # SAVE RESULTS TO JSON
    json_filename = "results/simulation_results.json"  # Path updated
    with open(json_filename, "w") as f:
        json.dump(experiment_results, f, indent=4)
    print(f"\n[SYSTEM] Results saved to {json_filename}")

    # TRIGGER VISUALIZATION AUTOMATICALLY
    print("[SYSTEM] Generating plots from new results...")
    try:
        visualizer.generate_all_visuals(json_filename)
        print("[SYSTEM] All visuals generated successfully.")
    except Exception as e:
        print(f"[ERROR] Could not generate visuals: {e}")