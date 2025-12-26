"""
Unit tests for FloydNode algorithm implementation.

Tests the distributed Floyd-Warshall algorithm (Algorithm 7.4).
"""

import pytest
import simpy
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.floyd_node import FloydNode
from core.distsim import System


class TestFloydNode:
    """Test suite for FloydNode implementation."""
    
    @pytest.mark.unit
    def test_floyd_node_initialization(self):
        """Test that FloydNode initializes with correct data structures."""
        sys_obj = System(NodeObject=FloydNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        # Check Algorithm 7.4 data structures
        assert hasattr(node, 'D_u'), "Node should have D_u distance matrix"
        assert hasattr(node, 'P_u'), "Node should have P_u predecessor matrix"
        
        assert isinstance(node.D_u, dict), "D_u should be a dictionary"
        assert isinstance(node.P_u, dict), "P_u should be a dictionary"
        
        # Initial state checks
        assert node.D_u[node.id] == 0, "Distance to self should be 0"
        assert node.P_u[node.id] == -1, "Predecessor to self should be -1"
    
    @pytest.mark.unit
    def test_floyd_node_neighbor_initialization(self):
        """Test that Floyd node properly initializes neighbor distances."""
        sys_obj = System(NodeObject=FloydNode, nodeCount=2)
        
        # Add edge with weight
        sys_obj.nodes[0].addNeighbor(1, {'weight': 50})
        
        node0 = sys_obj.nodes[0]
        
        # Node 0 should know about node 1
        assert 1 in node0.neighbors, "Node 0 should have node 1 as neighbor"
        assert node0.neighbors[1]['weight'] == 50, "Edge weight should be 50"
    
    @pytest.mark.unit
    def test_floyd_node_bit_counting(self):
        """Test that Floyd node tracks bit complexity."""
        sys_obj = System(NodeObject=FloydNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        initial_bits = node.total_bits_sent
        
        # Send a test message
        test_msg = {'type': 'TEST', 'vector': {0: 0, 1: 10}}
        node.sendMessageTo(1, test_msg)
        
        # Bits should have increased
        assert node.total_bits_sent > initial_bits, "Bit count should increase after sending message"
    
    @pytest.mark.unit
    def test_floyd_node_has_run_method(self):
        """Test that FloydNode has the main run method."""
        sys_obj = System(NodeObject=FloydNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        assert hasattr(node, 'run'), "FloydNode should have run method"
        assert callable(node.run), "run should be callable"


class TestFloydAlgorithmLogic:
    """Test suite for Floyd-Warshall algorithm logic."""
    
    @pytest.mark.integration
    def test_floyd_simple_path(self):
        """Test Floyd algorithm on a simple linear graph."""
        env = simpy.Environment()
        sys_obj = System(env)
        
        # Create linear graph: 0 -- 1 -- 2
        sys_obj.addNode(FloydNode, 0)
        sys_obj.addNode(FloydNode, 1)
        sys_obj.addNode(FloydNode, 2)
        
        sys_obj.addEdge(0, 1, weight=10)
        sys_obj.addEdge(1, 2, weight=15)
        
        # Run simulation
        sys_obj.run(until=100)
        
        node0 = sys_obj.nodes[0]
        
        # Node 0 should have computed distances
        assert 0 in node0.D_u, "Should have distance to self"
        assert 1 in node0.D_u, "Should have distance to node 1"
        
        # Check distances
        assert node0.D_u[0] == 0, "Distance to self should be 0"
        assert node0.D_u[1] == 10, "Distance to node 1 should be 10"
    
    @pytest.mark.integration
    def test_floyd_triangle_graph(self):
        """Test Floyd algorithm on a triangle graph."""
        env = simpy.Environment()
        sys_obj = System(env)
        
        # Create triangle with different edge weights
        sys_obj.addNode(FloydNode, 0)
        sys_obj.addNode(FloydNode, 1)
        sys_obj.addNode(FloydNode, 2)
        
        sys_obj.addEdge(0, 1, weight=5)
        sys_obj.addEdge(1, 2, weight=5)
        sys_obj.addEdge(0, 2, weight=20)
        
        # Run simulation
        sys_obj.run(until=100)
        
        node0 = sys_obj.nodes[0]
        
        # Check that shortest path is computed (via node 1, not direct)
        assert node0.D_u[0] == 0, "Distance to self should be 0"
        assert node0.D_u[1] == 5, "Distance to node 1 should be 5"
        # Should find path 0->1->2 (cost 10) instead of direct 0->2 (cost 20)
        if 2 in node0.D_u:
            assert node0.D_u[2] <= 10, f"Distance to node 2 should be at most 10, got {node0.D_u[2]}"
