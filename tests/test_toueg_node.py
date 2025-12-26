"""
Unit tests for TouegNode algorithm implementation.

Tests the Toueg's distributed shortest path algorithm (Algorithm 7.5).
"""

import pytest
import simpy
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from algorithms.toueg_node import TouegNode
from core.distsim import System


class TestTouegNode:
    """Test suite for TouegNode implementation."""
    
    @pytest.mark.unit
    def test_toueg_node_initialization(self):
        """Test that TouegNode initializes with correct data structures."""
        sys_obj = System(NodeObject=TouegNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        # Check Algorithm 7.5 data structures (Lines 1-2)
        assert hasattr(node, 'S_u'), "Node should have S_u set"
        assert hasattr(node, 'D_u'), "Node should have D_u dictionary"
        assert hasattr(node, 'Nb_u'), "Node should have Nb_u dictionary"
        
        assert isinstance(node.S_u, set), "S_u should be a set"
        assert isinstance(node.D_u, dict), "D_u should be a dictionary"
        assert isinstance(node.Nb_u, dict), "Nb_u should be a dictionary"
        
        # Initial state checks
        assert len(node.S_u) == 0, "S_u should start empty"
        assert node.D_u[node.id] == 0, "Distance to self should be 0"
        assert node.Nb_u[node.id] == -1, "Next hop to self should be -1"
    
    @pytest.mark.unit
    def test_toueg_node_neighbor_setup(self):
        """Test that neighbors are properly initialized with distances."""
        sys_obj = System(NodeObject=TouegNode, nodeCount=3)
        
        # Add edges with weights
        sys_obj.nodes[0].addNeighbor(1, {'weight': 100})
        sys_obj.nodes[1].addNeighbor(2, {'weight': 200})
        
        node0 = sys_obj.nodes[0]
        
        # After initialization, node 0 should know about its neighbors
        assert 1 in node0.neighbors, "Node 0 should have node 1 as neighbor"
        assert node0.neighbors[1]['weight'] == 100, "Edge weight should be 100"
    
    @pytest.mark.unit
    def test_toueg_node_bit_counting(self):
        """Test that message bit complexity is tracked correctly."""
        sys_obj = System(NodeObject=TouegNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        initial_bits = node.total_bits_sent
        
        # Send a test message
        test_msg = {'type': 'TEST', 'data': 'hello'}
        node.sendMessageTo(1, test_msg)
        
        # Bits should have increased
        assert node.total_bits_sent > initial_bits, "Bit count should increase after sending message"
    
    @pytest.mark.unit
    def test_toueg_node_has_run_method(self):
        """Test that TouegNode has the main run method."""
        sys_obj = System(NodeObject=TouegNode, nodeCount=1)
        
        node = sys_obj.nodes[0]
        
        assert hasattr(node, 'run'), "TouegNode should have run method"
        assert callable(node.run), "run should be callable"


class TestTouegAlgorithmLogic:
    """Test suite for Toueg algorithm logic and message flow."""
    
    @pytest.mark.integration
    def test_toueg_simple_triangle(self):
        """Test Toueg algorithm on a simple 3-node triangle graph."""
        sys_obj = System(NodeObject=TouegNode, nodeCount=3)
        
        # Add edges for triangle: 0 -- 1 -- 2
        #                           \______/
        sys_obj.nodes[0].addNeighbor(1, {'weight': 10})
        sys_obj.nodes[1].addNeighbor(0, {'weight': 10})
        sys_obj.nodes[1].addNeighbor(2, {'weight': 10})
        sys_obj.nodes[2].addNeighbor(1, {'weight': 10})
        sys_obj.nodes[0].addNeighbor(2, {'weight': 25})
        sys_obj.nodes[2].addNeighbor(0, {'weight': 25})
        
        # Run simulation
        sys_obj.env.run(until=100)
        
        node0 = sys_obj.nodes[0]
        
        # Node 0 should have computed distances to all nodes
        assert 0 in node0.D_u, "Should have distance to self"
        assert 1 in node0.D_u, "Should have distance to node 1"
        assert 2 in node0.D_u, "Should have distance to node 2"
        
        # Check shortest path distances
        assert node0.D_u[0] == 0, "Distance to self should be 0"
        assert node0.D_u[1] == 10, "Distance to node 1 should be 10"
        # Distance to node 2 should be 20 (via node 1), not 25 (direct)
        assert node0.D_u[2] == 20, f"Distance to node 2 should be 20, got {node0.D_u[2]}"
