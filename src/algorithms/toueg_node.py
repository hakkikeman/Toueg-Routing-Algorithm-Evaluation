from core.distsim import Node

class TouegNode(Node):
    """
    Implementation of Toueg's Algorithm (Algorithm 7.5).
    Reference: Erciyes, Distributed Graph Algorithms, Algorithm 7.5
    """
    def __init__(self, id, env, msgManager):
        Node.__init__(self, id, env, msgManager)
        
        # --- Algorithm 7.5 Data Structures (Lines 1-2) ---
        # 1: set of int Su, Du, Nbu
        # 2: Su <- empty set
        self.S_u = set()
        self.D_u = {self.id: 0}
        self.Nb_u = {self.id: -1} # Nbu in Toueg corresponds to Pu in Floyd
        
        self.total_bits_sent = 0

    def sendMessageTo(self, to, msgdict):
        """Calculates Bit Complexity based on message size."""
        bits = len(str(msgdict)) * 8
        self.total_bits_sent += bits
        super().sendMessageTo(to, msgdict)

    def run(self):
        """Main execution loop mapping Algorithm 7.5 logic."""
        
        # --- Initialization (Lines 3-10) ---
        yield self.env.timeout(1)
        
        # 3: for all v in V do
        for v in self.neighbors:
            weight = self.neighbors[v].get('weight', 100)
            # 6: else if {u,v} in E then
            # 7: Du[v] <- wuv, Nbu[v] <- v
            self.D_u[v] = weight
            self.Nb_u[v] = v
        # (Implicitly handles Lines 4-5 and 8-9)

        while True:
            yield self.mailbox.get(1)
            msg = self.receiveMessage()
            
            # --- PIVOT SELECTION (Lines 11-12) ---
            if msg['type'] == 'START_ROUND':
                # 12: pick w from V \ Su
                w = msg['pivot']
                if w in self.S_u: continue

                # --- PHASE 1: BUILD Tw (Lines 13-17) ---
                # 13: for all x in Neighbors(u) do
                parent_for_w = self.Nb_u.get(w, -1)
                
                for x in self.neighbors:
                    # 14: if Nbu[w] = x then send child(w) to x
                    if parent_for_w == x:
                        self.sendMessageTo(x, {'type': 'CHILD', 'pivot': w, 'sender': self.id})
                    # 15: else send nonchild(w) to x
                    else:
                        self.sendMessageTo(x, {'type': 'NONCHILD', 'pivot': w, 'sender': self.id})
                # 16-17: end if, end for

                # --- WAIT FOR STATUS (Lines 18-22) ---
                # 18: n_recvd <- 0
                n_recvd = 0
                total_neighbors = len(self.neighbors)
                my_children_in_Tw = []

                # 19: while n_recvd < |Neighbors(u)| do
                while n_recvd < total_neighbors:
                    yield self.mailbox.get(1)
                    status_msg = self.receiveMessage()
                    
                    # Ensure message is for current pivot (Logic integrity)
                    if status_msg.get('pivot') != w: continue 
                    if status_msg['type'] not in ['CHILD', 'NONCHILD']: continue

                    # 20: receive a child(w) or nonchild(w)
                    if status_msg['type'] == 'CHILD':
                        my_children_in_Tw.append(status_msg['sender'])
                    
                    # 21: n_recvd <- n_recvd + 1
                    n_recvd += 1
                # 22: end while

                # --- PHASE 2: DATA PROPAGATION & UPDATE (Lines 23-35) ---
                # 23: if Du[w] < infinity then
                if self.D_u.get(w, float('inf')) < float('inf'):
                    
                    pivot_vector_Dw = {}

                    # 24: if u != w then
                    if self.id != w:
                        # 25: receive Dw from Nbu[w]
                        # (We must wait for the parent to send the data)
                        if parent_for_w != -1:
                            received_data = False
                            while not received_data:
                                yield self.mailbox.get(1)
                                data_msg = self.receiveMessage()
                                if data_msg['type'] == 'PIVOT_DATA' and data_msg['pivot_src'] == w:
                                    pivot_vector_Dw = data_msg['vector']
                                    received_data = True
                    # Implicit else (if u == w): I am the source, use my D_u
                    else:
                        pivot_vector_Dw = self.D_u.copy()

                    # 27: for all x in Neighbors(u) that sent child(w) do send Dw to x
                    for child in my_children_in_Tw:
                        self.sendMessageTo(child, {
                            'type': 'PIVOT_DATA', 
                            'vector': pivot_vector_Dw, 
                            'pivot_src': w
                        })
                    # 28: end for

                    # 29-34: Update distance values (Relaxation)
                    # 30: if Du[w] + Dw[v] < Du[v] then
                    dist_u_w = self.D_u[w]
                    for v, dist_w_v in pivot_vector_Dw.items():
                        current_dist = self.D_u.get(v, float('inf'))
                        new_dist = dist_u_w + dist_w_v
                        
                        if new_dist < current_dist:
                            # 31: Du[v] <- Du[w] + Dw[v]
                            self.D_u[v] = new_dist
                            # 32: Nbu[v] <- Nbu[w]
                            self.Nb_u[v] = self.Nb_u[w]
                    # 33: end if
                # 35: end if

                # 36: Su <- Su U {w}
                self.S_u.add(w)