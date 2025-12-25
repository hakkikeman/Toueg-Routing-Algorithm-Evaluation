# Toueg Routing Algorithm Evaluation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![SimPy](https://img.shields.io/badge/SimPy-Discrete%20Event%20Simulation-green.svg)](https://simpy.readthedocs.io/)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Analysis-orange.svg)](https://networkx.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A comprehensive performance evaluation of Toueg's distributed shortest path algorithm (Algorithm 7.5) compared against the distributed Floyd-Warshall algorithm (Algorithm 7.4) using discrete-event simulation on real-world flight network data.**

---

## 📋 Abstract

This project implements and evaluates two fundamental distributed graph algorithms for computing all-pairs shortest paths in network topologies:

- **Toueg's Algorithm (Algorithm 7.5)**: A tree-based distributed shortest path algorithm with optimized message complexity
- **Distributed Floyd-Warshall (Algorithm 7.4)**: A flooding-based distance vector protocol

The evaluation is conducted through **discrete-event simulation** using the SimPy framework, with experiments performed on real-world flight network data from the OpenFlights dataset. The study investigates three critical dimensions:

1. **Correctness Validation**: Verifying algorithmic accuracy across varying network sizes
2. **Scalability Analysis**: Performance characterization under dense and sparse network topologies
3. **Complexity Comparison**: Message and bit complexity evaluation

This work is part of graduate-level research in **Distributed Algorithm Analysis and Design**, focusing on practical performance characteristics of theoretical distributed algorithms.

---

## ✨ Key Features

### 🔬 **Rigorous Algorithm Implementation**
- **Line-by-line mapping** of Toueg's Algorithm 7.5 from Erciyes' "Distributed Graph Algorithms"
- Faithful implementation of distributed Floyd-Warshall with relaxation-based flooding
- Comprehensive inline documentation linking code to theoretical algorithm steps

### 🌐 **Real-World Network Data**
- Integration with **OpenFlights** dataset (airports and routes)
- Geographic distance calculation using Haversine formula
- Support for both dense and sparse network topologies

### ⚙️ **Discrete-Event Simulation Framework**
- Custom-built distributed system simulator using **SimPy**
- Asynchronous message passing with mailbox-based communication
- Accurate message and bit complexity tracking

### 📊 **Comprehensive Experimental Suite**
- **Experiment 1**: Scalability testing (10-50 nodes)
- **Experiment 2**: Connectivity analysis (dense vs. sparse graphs)
- **Experiment 3**: Complexity comparison (message count and bit transmission)

### 📈 **Professional Visualization**
- Automated generation of publication-quality charts
- Network topology visualization with geographic coordinates
- Comparative performance analysis graphs

---

## 🏗️ Technical Architecture

### Project Structure

```
Toueg-Routing-Algorithm-Evaluation/
├── src/
│   ├── algorithms/
│   │   ├── toueg_node.py          # Toueg's Algorithm 7.5 implementation
│   │   └── floyd_node.py          # Distributed Floyd-Warshall (Algo 7.4)
│   ├── core/
│   │   └── distsim.py             # Discrete-event simulation framework
│   ├── utils/
│   │   ├── data_loader.py         # OpenFlights data processing
│   │   └── visualizer.py          # Chart generation and visualization
│   └── main_runner.py             # Experiment orchestration
├── data/
│   ├── airports.csv               # Airport geographic data
│   └── routes.csv                 # Flight route connections
├── results/
│   ├── *.png                      # Generated visualizations
│   └── simulation_results.json    # Experimental data
└── requirements.txt
```

### Core Components

#### 1. **Simulation Framework** (`core/distsim.py`)
- **System**: Manages global simulation state and node lifecycle
- **Node**: Base class for distributed algorithm nodes
- **MessageManager**: Handles asynchronous message delivery with configurable delays

#### 2. **Algorithm Implementations**

**Toueg's Algorithm** (`algorithms/toueg_node.py`)
- **Phase 1**: Pivot-based tree construction using parent-child relationships
- **Phase 2**: Distance vector propagation along the constructed tree
- **Optimization**: Minimizes redundant message transmission through structured communication

**Distributed Floyd-Warshall** (`algorithms/floyd_node.py`)
- **Flooding mechanism**: Each node broadcasts distance vectors to all neighbors
- **Relaxation**: Continuous distance table updates when better paths are discovered
- **Characteristic**: Higher message complexity due to unrestricted flooding

#### 3. **Data Processing** (`utils/data_loader.py`)
- Parses OpenFlights CSV data
- Constructs NetworkX graph with geographic edge weights
- Implements Haversine distance calculation for realistic routing costs

#### 4. **Visualization Engine** (`utils/visualizer.py`)
- Network topology rendering with Matplotlib
- Comparative bar charts for performance metrics
- Automated figure generation from JSON results

---

## 🧪 Experimental Methodology

### Dataset
- **Source**: OpenFlights (airports.csv, routes.csv)
- **Network Type**: Directed graph with weighted edges
- **Edge Weights**: Geographic distance in kilometers (Haversine formula)
- **Topology Variations**: Dense (original) and sparse (40% edge retention)

### Experiment Design

#### **Experiment 1: Scalability Analysis**
- **Objective**: Evaluate performance across varying network sizes
- **Node Counts**: 10, 20, 30, 40, 50
- **Metrics**: Execution time, message count, accuracy, average degree
- **Validation**: Comparison against NetworkX's all-pairs shortest path

#### **Experiment 2: Connectivity Stress Test**
- **Objective**: Assess robustness in sparse topologies
- **Configuration**: 10-node network with 40% edge retention
- **Purpose**: Evaluate algorithm behavior under reduced connectivity

#### **Experiment 3: Complexity Comparison**
- **Objective**: Quantify message and bit complexity
- **Network**: 10-node real-world topology
- **Metrics**: Total messages sent, total bits transmitted
- **Analysis**: Direct head-to-head comparison of both algorithms

---

## 📊 Results and Analysis

### Network Topology Visualization

![Real-World Network Topology](results/Network_Real_World_10_Nodes.png)
*Figure 1: 10-node flight network extracted from OpenFlights dataset with geographic edge weights*

---

### Performance Comparison: Toueg vs. Floyd-Warshall

![Algorithm Comparison](results/Comparison_Toueg_vs_Floyd.png)
*Figure 2: Comprehensive performance comparison across scalability, connectivity, and complexity dimensions*

**Key Findings:**
- **Toueg's Algorithm**: Demonstrates superior message efficiency through structured tree-based communication
- **Floyd-Warshall**: Exhibits higher message overhead due to flooding-based propagation
- **Accuracy**: Both algorithms achieve 100% correctness validation against NetworkX

---

### Execution Time Analysis

![Execution Time Comparison](results/Performance_Time_BAR.png)
*Figure 3: Execution time comparison for 10-node network*

**Observations:**
- Toueg's algorithm shows competitive execution times despite additional tree construction overhead
- Floyd-Warshall's flooding mechanism introduces processing delays due to message volume

---

### Message Complexity Analysis

![Message Complexity](results/Performance_Complexity_Messages_BAR.png)
*Figure 4: Total message count comparison*

**Analysis:**
- **Toueg**: O(n²) message complexity through controlled pivot-based propagation
- **Floyd-Warshall**: O(n³) message complexity due to unrestricted flooding
- **Practical Impact**: Toueg achieves ~60% reduction in message count for 10-node network

---

### Connectivity Analysis: Dense vs. Sparse

![Connectivity Analysis](results/Connectivity_Analysis_Dense_vs_Sparse.png)
*Figure 5: Performance under varying connectivity conditions*

**Insights:**
- Both algorithms maintain correctness in sparse topologies
- Message count scales with network density
- Toueg's structured approach provides consistent performance across connectivity levels

---

## 🚀 Installation and Usage

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/hakkikeman/Toueg-Routing-Algorithm-Evaluation.git
cd Toueg-Routing-Algorithm-Evaluation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running Experiments

**Execute all experiments:**
```bash
python src/main_runner.py
```

**Output:**
- Console logs with detailed experiment progress
- `results/simulation_results.json`: Raw experimental data
- `results/*.png`: Generated visualization charts

### Customization

**Modify network size** (in `src/main_runner.py`):
```python
for count in [10, 20, 30, 40, 50]:  # Adjust node counts
    run_experiment_basic(num_nodes=count, ...)
```

**Adjust sparsity** (in `src/main_runner.py`):
```python
make_graph_sparse(G, keep_prob=0.4)  # Change edge retention probability
```

---

## 📚 Theoretical Background

### Toueg's Algorithm (Algorithm 7.5)

**Reference**: Erciyes, K. (2018). *Distributed Graph Algorithms for Computer Networks*. Algorithm 7.5.

**Key Characteristics:**
- **Approach**: Pivot-based tree construction with distance vector propagation
- **Message Complexity**: O(n² log n)
- **Communication Pattern**: Structured parent-child relationships minimize redundancy

**Algorithm Phases:**
1. **Pivot Selection**: Iteratively select unprocessed nodes as pivots
2. **Tree Construction**: Build shortest-path tree rooted at pivot
3. **Distance Propagation**: Broadcast distance vectors along tree edges
4. **Relaxation**: Update local routing tables with improved paths

### Distributed Floyd-Warshall (Algorithm 7.4)

**Reference**: Erciyes, K. (2018). *Distributed Graph Algorithms for Computer Networks*. Algorithm 7.4.

**Key Characteristics:**
- **Approach**: Flooding-based distance vector protocol
- **Message Complexity**: O(n³)
- **Communication Pattern**: Unrestricted broadcast to all neighbors

**Algorithm Mechanism:**
1. **Initialization**: Each node knows direct neighbor distances
2. **Flooding**: Nodes broadcast distance vectors upon receiving updates
3. **Relaxation**: Continuous distance table updates via Bellman-Ford relaxation
4. **Convergence**: Algorithm terminates when no further improvements occur

---

## 🎯 Conclusions

### Research Findings

1. **Correctness**: Both algorithms achieve 100% accuracy across all tested configurations
2. **Message Efficiency**: Toueg's algorithm demonstrates ~60% message reduction compared to Floyd-Warshall
3. **Scalability**: Toueg maintains superior performance as network size increases
4. **Robustness**: Both algorithms handle sparse topologies effectively

### Practical Implications

- **Toueg's Algorithm** is preferable for:
  - Large-scale networks where message overhead is critical
  - Bandwidth-constrained environments
  - Applications requiring predictable communication patterns

- **Floyd-Warshall** may be suitable for:
  - Small networks where simplicity is prioritized
  - Scenarios requiring rapid convergence
  - Fault-tolerant systems benefiting from redundant message paths

### Future Work

- **Dynamic Networks**: Extend evaluation to networks with link failures and topology changes
- **Asynchronous Models**: Investigate performance under varying message delays
- **Hybrid Approaches**: Explore algorithms combining tree-based and flooding mechanisms
- **Real-World Deployment**: Implement on actual distributed systems (e.g., IoT networks)

---

## 📖 References

1. Erciyes, K. (2018). *Distributed Graph Algorithms for Computer Networks*. Springer.
2. Lynch, N. A. (1996). *Distributed Algorithms*. Morgan Kaufmann.
3. OpenFlights Dataset: https://openflights.org/data.html
4. SimPy Documentation: https://simpy.readthedocs.io/
5. NetworkX Documentation: https://networkx.org/documentation/

---

## 👤 Author

**Hakkı Keman**  
M.Sc. in Computer Engineering - Ege University
Distributed Algorithm Analysis and Design

📧 Contact: kemangs2009@outlook.com         
🔗 LinkedIn: www.linkedin.com/in/hakki-keman  
🐙 GitHub: https://github.com/hakkikeman

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Course**: Distributed Algorithm Analysis and Design
- **Dataset**: OpenFlights community for maintaining comprehensive flight network data
- **Frameworks**: SimPy and NetworkX development teams
- **Reference**: Prof. Kayhan Erciyes for foundational algorithm descriptions

---

<div align="center">

**⭐ If you find this research useful, please consider starring the repository! ⭐**

</div>
