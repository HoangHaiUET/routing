####################################################
# DVrouter.py
# Name: Nguyen Van Hoang HaiHai
# HUID: 23020660
#####################################################

from router import Router
from packet import Packet
import json

class DVrouter(Router):
    """Distance vector routing protocol implementation."""

    def __init__(self, addr, heartbeat_time):
        Router.__init__(self, addr)  # Initialize base class
        self.heartbeat_time = heartbeat_time
        self.last_time = 0
        
        # Distance vector cho các điểm đích
        self.distance_vector = {self.addr: 0}
        
        # Bảng chuyển tiếp: {đích: (khoảng cách, cổng)}
        self.forwarding_table = {}
        
        # Thông tin láng giềng: {láng giềng: khoảng cách trực tiếp}
        self.neighbors = {}

    def handle_packet(self, port, packet):
        """Process incoming packet."""
        if packet.is_traceroute:
            # Nếu biết đường đi tới đích, chuyển tiếp gói tin
            if packet.dst_addr in self.forwarding_table:
                next_port = self.forwarding_table[packet.dst_addr][1]
                self.send(next_port, packet)
        else:
            # Gói tin định tuyến chứa vector khoảng cách
            try:
                # Phân tích vector khoảng cách từ gói tin
                received_vector = json.loads(packet.content)
                neighbor = packet.src_addr
                neighbor_distance = self.neighbors.get(neighbor, float('inf'))

                # Kiểm tra và cập nhật vector khoảng cách
                vector_changed = False
                for dst, distance in received_vector.items():
                    if dst == self.addr:
                        continue
                    
                    new_distance = neighbor_distance + distance
                    
                    # Cập nhật nếu đường đi mới tốt hơn
                    if (dst not in self.distance_vector or 
                        new_distance < self.distance_vector.get(dst, float('inf'))):
                        self.distance_vector[dst] = new_distance
                        self.forwarding_table[dst] = (new_distance, port)
                        vector_changed = True

                # Nếu vector thay đổi, phát quảng bá
                if vector_changed:
                    self.broadcast_distance_vector()

            except (json.JSONDecodeError, TypeError):
                pass

    def handle_new_link(self, port, endpoint, cost):
        """Handle new link."""
        # Cập nhật láng giềng và khoảng cách trực tiếp
        self.neighbors[endpoint] = cost
        
        # Cập nhật vector khoảng cách
        if endpoint not in self.distance_vector or cost < self.distance_vector[endpoint]:
            self.distance_vector[endpoint] = cost
            self.forwarding_table[endpoint] = (cost, port)
        
        # Phát quảng bá vector khoảng cách
        self.broadcast_distance_vector()

    def handle_remove_link(self, port):
        """Handle removed link."""
        # Tìm láng giềng bị mất kết nối
        removed_neighbor = None
        for neighbor, neighbor_port in self.links.items():
            if neighbor_port == port:
                removed_neighbor = neighbor
                break

        if removed_neighbor:
            # Xóa láng giềng khỏi danh sách
            del self.neighbors[removed_neighbor]
            
            # Loại bỏ các đích đi qua láng giềng này
            destinations_to_remove = [
                dst for dst, (dist, via_port) in self.forwarding_table.items()
                if via_port == port
            ]
            
            for dst in destinations_to_remove:
                del self.distance_vector[dst]
                del self.forwarding_table[dst]
            
            # Phát quảng bá vector khoảng cách mới
            self.broadcast_distance_vector()

    def handle_time(self, time_ms):
        """Broadcast distance vector periodically."""
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            self.broadcast_distance_vector()

    def broadcast_distance_vector(self):
        """Broadcast the current distance vector to all neighbors."""
        for port, link in self.links.items():
            neighbor = link.e2 if link.e1 == self.addr else link.e1
            
            # Tạo gói tin với vector khoảng cách
            packet = Packet(
                Packet.ROUTING, 
                self.addr, 
                neighbor, 
                json.dumps(self.distance_vector)
            )
            
            # Gửi tới láng giềng
            self.send(port, packet)

    def __repr__(self):
        """Debugging representation."""
        return (f"DVrouter(addr={self.addr}, "
                f"distance_vector={self.distance_vector}, "
                f"forwarding_table={self.forwarding_table})")