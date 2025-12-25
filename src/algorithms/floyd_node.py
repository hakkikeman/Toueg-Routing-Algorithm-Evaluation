from core.distsim import Node

class FloydNode(Node):
    """
    Implementation of Distributed Floyd-Warshall Algorithm (Algorithm 7.4).
    CORRECTED LOGIC:
    - Allows re-broadcasting if a 'better' path is found (Relaxation).
    - This creates the characteristic 'message explosion' of Distance Vector protocols.
    """
    def __init__(self, id, env, msgManager):
        Node.__init__(self, id, env, msgManager)
        
        # S_u: Keeps track of pivots we have heard from at least once
        self.S_u = set()               
        self.D_u = {self.id: 0}        
        self.P_u = {self.id: -1}       
        self.total_bits_sent = 0

    def sendMessageTo(self, to, msgdict):
        bits = len(str(msgdict)) * 8
        self.total_bits_sent += bits
        super().sendMessageTo(to, msgdict)

    def run(self):
        yield self.env.timeout(1)
        
        # Init weights
        for v in self.neighbors:
            weight = self.neighbors[v].get('weight', 100)
            self.D_u[v] = weight
            self.P_u[v] = v
        
        while True:
            yield self.mailbox.get(1)
            msg = self.receiveMessage()
            m_type = msg['type']
            
            if m_type == 'START_ROUND':
                w = msg['pivot']
                
                # If I am pivot, initiate flood with my distance vector
                if self.id == w:
                    self.S_u.add(w)
                    # Pivot broadcasts its own distance vector
                    self.broadcast_vector(w, self.D_u)
                # If I'm NOT the pivot, I still need to be ready to receive FLOOD_DW
                # The algorithm continues in the FLOOD_DW handler below

            elif m_type == 'FLOOD_DW':
                w = msg['pivot_src']
                D_w = msg['vector']  # This is the SENDER's distance vector (not necessarily pivot's)
                sender = msg['sender']
                
                # Check 1: Is this the first time I hear about pivot w?
                first_time = (w not in self.S_u)
                
                if first_time:
                    self.S_u.add(w)
                
                # Check 2: Does this message improve my routing table?
                improved = self.relax(w, D_w, sender)
                
                # CRITICAL FIX: After updating our table, broadcast OUR updated D_u
                # Each node propagates its own distances, not the pivot's
                # This is how distributed Floyd-Warshall works: flooding with updates
                if first_time or improved:
                    # Broadcast our own updated distance vector
                    self.broadcast_vector(w, self.D_u)




    def broadcast_vector(self, w, vector):
        """Broadcasts the distance vector to ALL neighbors."""
        for neighbor in self.neighbors:
            self.sendMessageTo(neighbor, {
                'type': 'FLOOD_DW',
                'pivot_src': w,
                'vector': vector.copy(),
                'sender': self.id
            })

    def relax(self, w, D_sender, sender):
        """
        Updates local distances following distributed Floyd-Warshall logic.
        
        IMPORTANT: D_sender is the SENDER's distance table, not the pivot's!
        Each node broadcasts its own D_u after updating.
        
        Algorithm 7.4 Line 19 adapted for distributed flooding:
        For each destination v: Du[v] = min(Du[v], dist(u, sender) + D_sender[v])
        
        Returns True if ANY value in the table improved.
        """
        updated = False
        
        # Get edge weight to sender
        dist_to_sender = self.neighbors.get(sender, {}).get('weight', float('inf'))
        
        # Update distances using sender's table
        # For each destination v in sender's table:
        # New path: me -> sender -> v
        # Cost: dist(me, sender) + D_sender[v]
        
        for v, dist_sender_to_v in D_sender.items():
            current_dist_to_v = self.D_u.get(v, float('inf'))
            
            # New distance via sender
            new_dist_to_v = dist_to_sender + dist_sender_to_v
            
            # If this path is better, update
            if new_dist_to_v < current_dist_to_v:
                self.D_u[v] = new_dist_to_v
                self.P_u[v] = sender  # Next hop to reach v is sender
                updated = True
        
        return updated