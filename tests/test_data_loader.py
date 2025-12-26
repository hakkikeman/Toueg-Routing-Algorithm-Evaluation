"""
Unit tests for data loading utilities.

Tests the haversine distance calculation and flight graph construction
from the OpenFlights dataset.
"""

import pytest
import math
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.data_loader import haversine_distance, load_flight_graph


class TestHaversineDistance:
    """Test suite for haversine distance calculations."""
    
    @pytest.mark.unit
    def test_haversine_same_location(self):
        """Distance between same coordinates should be 0."""
        distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        assert distance == 0, "Distance between identical points should be 0"
    
    @pytest.mark.unit
    def test_haversine_known_distance(self):
        """Test with known city pair: Istanbul to Ankara."""
        # Istanbul: 41.0082° N, 28.9784° E
        # Ankara: 39.9334° N, 32.8597° E
        # Approximate distance: ~350 km
        distance = haversine_distance(41.0082, 28.9784, 39.9334, 32.8597)
        assert 340 <= distance <= 360, f"Istanbul-Ankara distance should be ~350km, got {distance}km"
    
    @pytest.mark.unit
    def test_haversine_new_york_london(self):
        """Test with known intercontinental distance: New York to London."""
        # New York: 40.7128° N, 74.0060° W
        # London: 51.5074° N, 0.1278° W
        # Approximate distance: ~5570 km
        distance = haversine_distance(40.7128, -74.0060, 51.5074, -0.1278)
        assert 5500 <= distance <= 5600, f"NYC-London distance should be ~5570km, got {distance}km"
    
    @pytest.mark.unit
    def test_haversine_returns_integer(self):
        """Haversine function should return an integer."""
        distance = haversine_distance(0, 0, 1, 1)
        assert isinstance(distance, int), "Distance should be returned as integer"
    
    @pytest.mark.unit
    def test_haversine_positive_result(self):
        """Distance should always be positive."""
        distance = haversine_distance(10, 20, -10, -20)
        assert distance >= 0, "Distance should always be non-negative"


class TestLoadFlightGraph:
    """Test suite for flight graph construction."""
    
    @pytest.mark.unit
    def test_load_flight_graph_file_not_found(self):
        """Should return None when data files don't exist."""
        G = load_flight_graph(
            routes_file='nonexistent_routes.csv',
            airports_file='nonexistent_airports.csv',
            num_nodes=10
        )
        assert G is None, "Should return None when files don't exist"
    
    @pytest.mark.integration
    def test_load_flight_graph_structure(self):
        """Test graph structure with real data files."""
        # This test requires actual data files to exist
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        routes_file = os.path.join(data_dir, 'routes.csv')
        airports_file = os.path.join(data_dir, 'airports.csv')
        
        # Skip if data files don't exist
        if not (os.path.exists(routes_file) and os.path.exists(airports_file)):
            pytest.skip("Data files not found, skipping integration test")
        
        G = load_flight_graph(routes_file, airports_file, num_nodes=10)
        
        if G is not None:
            # Graph should have nodes
            assert len(G.nodes()) > 0, "Graph should have at least one node"
            
            # Graph should have edges
            assert len(G.edges()) > 0, "Graph should have at least one edge"
            
            # All edges should have weights
            for u, v in G.edges():
                assert 'weight' in G[u][v], f"Edge ({u}, {v}) should have a weight"
                assert G[u][v]['weight'] > 0, f"Edge weight should be positive"
    
    @pytest.mark.integration
    def test_load_flight_graph_connectivity(self):
        """Verify that loaded graph is weakly connected."""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        routes_file = os.path.join(data_dir, 'routes.csv')
        airports_file = os.path.join(data_dir, 'airports.csv')
        
        if not (os.path.exists(routes_file) and os.path.exists(airports_file)):
            pytest.skip("Data files not found, skipping integration test")
        
        import networkx as nx
        G = load_flight_graph(routes_file, airports_file, num_nodes=10)
        
        if G is not None and len(G.nodes()) > 0:
            # Graph should be weakly connected (for directed graphs)
            assert nx.is_weakly_connected(G), "Graph should be weakly connected"
    
    @pytest.mark.integration
    def test_load_flight_graph_node_count(self):
        """Verify that graph has approximately the requested number of nodes."""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        routes_file = os.path.join(data_dir, 'routes.csv')
        airports_file = os.path.join(data_dir, 'airports.csv')
        
        if not (os.path.exists(routes_file) and os.path.exists(airports_file)):
            pytest.skip("Data files not found, skipping integration test")
        
        requested_nodes = 15
        G = load_flight_graph(routes_file, airports_file, num_nodes=requested_nodes)
        
        if G is not None:
            # Should have nodes (may be less than requested if connectivity filtering applied)
            assert 1 <= len(G.nodes()) <= requested_nodes, \
                f"Graph should have between 1 and {requested_nodes} nodes"
