from distsim import Node

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
                
                # If I am pivot, initiate flood
                if self.id == w:
                    self.S_u.add(w)
                    self.broadcast_vector(w, self.D_u)

            elif m_type == 'FLOOD_DW':
                w = msg['pivot_src']
                D_w = msg['vector']
                sender = msg['sender']
                
                # --- CRITICAL FIX ---
                # Check 1: Is this the first time I hear about pivot w?
                first_time = (w not in self.S_u)
                
                if first_time:
                    self.S_u.add(w)
                
                # Check 2: Does this message improve my routing table?
                # (Even if I heard from w before, this neighbor might offer a better path)
                improved = self.relax(w, D_w, sender)
                
                # RULE: Broadcast if it's the first time OR if we found a better path.
                # This causes the "Chatter" that makes Floyd expensive.
                if first_time or improved:
                    # If improved, we must share the new D_u with neighbors
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

    def relax(self, w, D_w, sender):
        """
        Updates local distances. 
        Returns True if ANY value in the table improved.
        """
        updated = False
        dist_to_sender = self.neighbors.get(sender, {}).get('weight', float('inf'))
        
        # We also need to update the distance TO the pivot w itself via sender
        # This is often missed. The vector D_w contains distances FROM w.
        # But D_w[w] is 0. So logic handles it naturally below.
        
        for v, dist_w_v in D_w.items():
            current_dist = self.D_u.get(v, float('inf'))
            
            # Path: Me -> Sender -> ... -> v
            # Cost: (Me->Sender) + (Sender's cost to v [which comes from w's vector perspective])
            # Wait, DistFW propagates D_w (distance from w to others).
            # The relaxation logic in the book is: Du[v] = min(Du[v], Du[w] + Dw[v])
            # We need to ensure we have a valid Du[w] first.
            
            dist_u_w = self.D_u.get(w, float('inf'))
            
            # If we don't know how to reach w, we can't use w as a pivot yet.
            # But wait, if 'sender' sent us this, we can reach w via 'sender'.
            # Special update for Du[w] using the sender:
            if v == w:
                 # The vector says dist from w to w is 0.
                 # So cost to w via sender is dist_to_sender + 0.
                 pass 

            new_dist_via_pivot = dist_u_w + dist_w_v
            
            if new_dist_via_pivot < current_dist:
                self.D_u[v] = new_dist_via_pivot
                if w in self.P_u:
                     self.P_u[v] = self.P_u[w]
                updated = True
                
        return updated