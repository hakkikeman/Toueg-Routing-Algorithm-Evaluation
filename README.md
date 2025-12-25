# Toueg vs. Floyd: Distributed Routing Algorithm Evaluation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![SimPy](https://img.shields.io/badge/SimPy-Discrete%20Event%20Simulation-orange.svg)](https://simpy.readthedocs.io/)

## 📖 About the Project

This project presents a **comprehensive comparative analysis** of two fundamental routing algorithms applied to distributed systems: **Toueg's Distributed Shortest Path Algorithm** and the **Floyd-Warshall All-Pairs Shortest Path Algorithm**. 

Using a custom-built **discrete event simulator** and **real-world airline network data**, this research evaluates the performance, message complexity, and robustness of both algorithms under various network topologies. The simulation framework models asynchronous message passing, network delays, and distributed computation to provide insights into algorithm behavior in realistic distributed environments.

**Key Insight:** While Floyd-Warshall offers simplicity and completeness, Toueg's algorithm demonstrates superior efficiency in message-passing distributed systems, making it ideal for large-scale, dynamic network topologies.

---

## ✨ Key Features

- **🌐 Distributed System Simulation**: Custom discrete event simulator (`distsim.py`) built with SimPy for realistic asynchronous message-passing environments
- **📊 Real-World Graph Data**: Analysis performed on actual airline network datasets (airports and routes) for practical relevance
- **⚡ Performance Benchmarking**: Comprehensive comparison across multiple dimensions:
  - **Message Complexity**: Total number of messages exchanged during computation
  - **Time Complexity**: Execution time and convergence speed
  - **Network Connectivity**: Algorithm robustness in dense vs. sparse network topologies
- **📈 Visual Analytics**: Detailed charts and network visualizations for intuitive understanding
- **🔬 Algorithmic Implementations**: 
  - `toueg_node.py`: Distributed implementation of Toueg's algorithm with asynchronous message handling
  - `floyd_node.py`: Distributed adaptation of Floyd-Warshall for comparative analysis

---

## 📊 Simulation Results & Analysis

### Network Topology Visualization

![Real-World Network Topology](results/Network_Real_World_10_Nodes.png)

**Figure 1: Real-World Airline Network (10 Nodes)** - This visualization showcases the actual network topology used in the simulation, derived from real airline route data. Node sizes represent connectivity degree, and edge weights represent distances or connection costs.

---

### Overall Algorithm Comparison

![Toueg vs Floyd Comparison](results/Comparison_Toueg_vs_Floyd.png)

**Figure 2: Comprehensive Algorithm Comparison** - A holistic view comparing Toueg's and Floyd-Warshall algorithms across multiple performance metrics. This chart highlights the trade-offs between distributed message-passing efficiency (Toueg) and centralized computation simplicity (Floyd-Warshall).

---

### Execution Time Analysis

![Performance Time Comparison](results/Performance_Time_BAR.png)

**Figure 3: Execution Time Performance** - Bar chart comparing the wall-clock execution time of both algorithms. Toueg's algorithm demonstrates competitive performance despite the overhead of distributed message passing, particularly beneficial in scenarios where computation can be parallelized across nodes.

---

### Message Complexity Analysis

![Message Complexity Comparison](results/Performance_Complexity_Messages_BAR.png)

**Figure 4: Message Overhead Comparison** - This critical metric reveals the total number of messages exchanged during algorithm execution. Toueg's algorithm shows optimized message complexity, making it significantly more efficient for bandwidth-constrained distributed systems compared to naive distributed implementations.

---

### Network Robustness Testing

![Connectivity Analysis](results/Connectivity_Analysis_Dense_vs_Sparse.png)

**Figure 5: Dense vs. Sparse Network Performance** - Analysis of algorithm behavior under varying network densities. This chart demonstrates how each algorithm scales with network connectivity, revealing Toueg's superior adaptability to sparse networks where message efficiency is paramount.

---

## 🏗️ Technical Architecture

### Project Structure

```
Toueg-Routing-Algorithm-Evaluation/
│
├── src/
│   ├── algorithms/
│   │   ├── toueg_node.py          # Toueg's distributed algorithm implementation
│   │   └── floyd_node.py          # Floyd-Warshall distributed adaptation
│   │
│   ├── core/
│   │   └── distsim.py             # Custom discrete event simulator (SimPy-based)
│   │
│   ├── utils/                     # Helper functions for data processing and visualization
│   │
│   └── main_runner.py             # Main execution script and experiment orchestrator
│
├── data/
│   ├── airports.csv               # Real-world airport node data
│   └── routes.csv                 # Real-world airline route edge data
│
├── results/                       # Generated visualizations and analysis charts
│
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

### Core Components

#### 🔧 Distributed Simulator (`distsim.py`)
A custom-built discrete event simulation framework that models:
- **Asynchronous Message Passing**: Realistic network delays and message ordering
- **Event-Driven Architecture**: Efficient simulation of concurrent node operations
- **Network Topology Management**: Dynamic graph structures with configurable parameters
- **Performance Metrics Collection**: Automated tracking of messages, time, and convergence

#### 🧮 Algorithm Implementations
- **Toueg Node**: Implements distributed shortest path computation using neighbor-to-neighbor message exchange with distance vector updates
- **Floyd Node**: Distributed version of the all-pairs shortest path algorithm adapted for message-passing environments

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/hakkikeman/toueg-routing-algorithm-evaluation.git
   cd toueg-routing-algorithm-evaluation
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - `simpy` - Discrete event simulation framework
   - `networkx` - Graph data structures and algorithms
   - `pandas` - Data manipulation and analysis
   - `matplotlib` - Visualization and plotting
   - `numpy` - Numerical computing

3. **Run the Simulation**
   ```bash
   python src/main_runner.py
   ```

4. **View Results**
   
   After execution, analysis charts will be generated in the `results/` directory. The console will display performance metrics and convergence statistics.

### Configuration Options

You can modify simulation parameters in `main_runner.py`:
- Network size (number of nodes)
- Network density (edge probability)
- Message delay distributions
- Algorithm-specific parameters

---

## 🎯 Conclusion & Key Findings

### When to Use Toueg's Algorithm
✅ **Distributed environments** where nodes operate independently  
✅ **Large-scale networks** where centralized computation is impractical  
✅ **Bandwidth-constrained systems** requiring minimal message overhead  
✅ **Dynamic topologies** where routes change frequently  

### When to Use Floyd-Warshall
✅ **Centralized systems** with complete network visibility  
✅ **Small to medium networks** where O(n³) complexity is acceptable  
✅ **Static topologies** requiring all-pairs shortest paths  
✅ **Scenarios** where simplicity and completeness outweigh message efficiency  

### Research Insights

The empirical analysis demonstrates that **Toueg's algorithm achieves superior message efficiency** (up to 40% reduction in message overhead) while maintaining competitive execution times. This makes it particularly well-suited for modern distributed systems such as:
- Software-Defined Networks (SDN)
- Internet of Things (IoT) routing
- Peer-to-peer networks
- Distributed databases and consensus systems

However, Floyd-Warshall remains valuable for scenarios requiring guaranteed all-pairs shortest paths with predictable behavior, especially in smaller, stable network topologies.

---

## 👨‍💻 Author

**Hakkı Keman**

- 💼 [LinkedIn](www.linkedin.com/in/hakki-keman)
- 🐙 [GitHub](https://github.com/hakkikeman)
- 📧 Contact: [kemangs2009@outlook.com]

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## � Data Sources

This research utilizes real-world airline network data to ensure practical relevance and realistic topology characteristics:

- **Dataset**: [Airports, Airlines, Planes and Routes (2024 Update)](https://www.kaggle.com/datasets/ahmadrafiee/airports-airlines-planes-and-routes-update-2024)
- **Author**: Ahmad Rafiee
- **Platform**: Kaggle
- **Description**: Comprehensive aviation dataset containing global airport locations, airline routes, and network connectivity information
- **Usage**: The `airports.csv` and `routes.csv` files provide the graph structure (nodes and edges) for algorithm evaluation

---

## 🙏 Acknowledgments

- Real-world airline data provided by Ahmad Rafiee via Kaggle
- SimPy discrete event simulation framework
- NetworkX graph library for network analysis
- Research inspired by foundational work in distributed algorithms by Sam Toueg and Robert Floyd

---

## 📚 References

- Toueg, S. (1980). "An All-Pairs Shortest Path Distributed Algorithm"
- Floyd, R. W. (1962). "Algorithm 97: Shortest Path"
- Warshall, S. (1962). "A Theorem on Boolean Matrices"

---

<div align="center">

**⭐ If you find this research useful, please consider starring the repository! ⭐**

</div>
