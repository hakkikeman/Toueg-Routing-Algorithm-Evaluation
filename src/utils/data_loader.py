import pandas as pd
import networkx as nx
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return int(R * c)

def load_flight_graph(routes_file='data/routes.csv', airports_file='data/airports.csv', num_nodes=20):
    """
    Loads flight data from CSV files and constructs a NetworkX DiGraph.
    """
    print(f"--- Loading Dataset: {routes_file} & {airports_file} ---")
    
    try:
        # 1. Load Airports Data
        df_airports = pd.read_csv(airports_file, low_memory=False)
        df_airports.columns = df_airports.columns.str.strip()
        
        airport_locs = {}
        for _, row in df_airports.iterrows():
            try:
                aid = int(row['Airport ID'])
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                airport_locs[aid] = (lat, lon)
            except (ValueError, KeyError):
                continue
                
        # 2. Load Routes Data
        df_routes = pd.read_csv(routes_file, low_memory=False)
        df_routes.columns = df_routes.columns.str.strip()
        
        # Clean invalid IDs
        df_routes = df_routes[pd.to_numeric(df_routes['Source airport ID'], errors='coerce').notnull()]
        df_routes = df_routes[pd.to_numeric(df_routes['Destination airport ID'], errors='coerce').notnull()]
        
        # 3. Filter Top N Most Active Airports
        top_airports = df_routes['Source airport ID'].astype(int).value_counts().head(num_nodes).index.tolist()
        
        # 4. Construct the Graph
        G = nx.DiGraph()
        for aid in top_airports:
            G.add_node(aid)
            
        for _, row in df_routes.iterrows():
            src = int(row['Source airport ID'])
            dst = int(row['Destination airport ID'])
            
            if src in top_airports and dst in top_airports:
                if src in airport_locs and dst in airport_locs:
                    lat1, lon1 = airport_locs[src]
                    lat2, lon2 = airport_locs[dst]
                    dist = haversine_distance(lat1, lon1, lat2, lon2)
                    
                    if not G.has_edge(src, dst):
                        G.add_edge(src, dst, weight=dist)
                    else:
                        old_w = G[src][dst]['weight']
                        if dist < old_w:
                            G[src][dst]['weight'] = dist

        if len(G) > 0:
            largest_cc = max(nx.weakly_connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()
            
        mapping = {old_id: new_id for new_id, old_id in enumerate(G.nodes())}
        nx.set_node_attributes(G, {node: str(node) for node in G.nodes()}, 'original_id')
        G = nx.relabel_nodes(G, mapping)

        print(f"Graph Constructed Successfully: {len(G.nodes)} Nodes, {len(G.edges)} Edges.")
        return G

    except Exception as e:
        print(f"ERROR: Failed to load dataset. Details: {e}")
        return None