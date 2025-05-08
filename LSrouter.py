####################################################
# LSrouter.py
# Name: Nguyen Van Hoang Hai
# HUID: 23020660
#####################################################

from router import Router
from packet import Packet
import heapq


class LSrouter(Router):
    """Link state routing protocol implementation.

    Add your own class fields and initialization code (e.g. to create forwarding table
    data structures). See the `Router` base class for docstrings of the methods to
    override.

    Thêm các thuộc tính và mã khởi tạo của lớp theo ý bạn (ví dụ: để tạo cấu trúc dữ liệu bảng chuyển tiếp). Xem lớp cơ sở Router để biết mô tả các phương thức cần ghi đè."


    """

    def __init__(self, addr, heartbeat_time):
        Router.__init__(self, addr)  # Initialize base class - DO NOT REMOVE
        self.heartbeat_time = heartbeat_time
        self.last_time = 0
        # TODO
        #   add your own class fields and initialization code here

        self.lsdb = (
            {}
        )  # Link state database: {router_addr: (seq_num, {neighbor: cost})}
        self.seq_nums = {}  # Latest sequence number seen from each router
        self.forwarding_table = {}  # {destination: port}
        self.topology = {}  # {neighbor: cost}
        self.ports = {}  # {neighbor: port}

        # Initialize own LSDB entry
        self.lsdb[self.addr] = (0, {})  # Sequence number 0 and empty neighbors
        pass

    def handle_packet(self, port, packet):
        if packet.is_traceroute:
            # Đây là gói tin dữ liệu, dùng bảng định tuyến để gửi đi
            dst = packet.dst_addr
            if dst in self.forwarding_table:
                out_port = self.forwarding_table[dst]
                self.send(out_port, packet)
        else:
            # Đây là gói tin routing từ các router khác
            try:
                origin, seq, neighbors_str = packet.content.split("|")
                seq = int(seq)
                neighbors = eval(neighbors_str)
            except Exception:
                return  # Gói lỗi

            # Nếu đã có thông tin mới hơn, bỏ qua
            if origin in self.seq_nums and seq <= self.seq_nums[origin]:
                return

            # Cập nhật LSDB và seq number
            self.seq_nums[origin] = seq
            self.lsdb[origin] = (seq, neighbors)

            # Tính lại bảng định tuyến
            self.compute_forwarding_table()

            # Broadcast lại gói tin này tới các router khác (trừ nơi nhận)
            for p, link in self.links.items():
                if p != port:
                    self.send(p, packet)
            pass

    def handle_new_link(self, port, endpoint, cost):
        self.topology[endpoint] = cost
        self.ports[endpoint] = port

        # Tăng sequence number
        seq = self.lsdb[self.addr][0] + 1
        self.lsdb[self.addr] = (seq, dict(self.topology))
        self.seq_nums[self.addr] = seq

        self.compute_forwarding_table()
        self.broadcast_link_state()
        pass

    def handle_remove_link(self, port):
        # Tìm endpoint bị xóa
        endpoint = None
        for node, p in self.ports.items():
            if p == port:
                endpoint = node
                break

        if endpoint:
            del self.topology[endpoint]
            del self.ports[endpoint]

            seq = self.lsdb[self.addr][0] + 1
            self.lsdb[self.addr] = (seq, dict(self.topology))
            self.seq_nums[self.addr] = seq

            self.compute_forwarding_table()
            self.broadcast_link_state()

        pass

    def handle_time(self, time_ms):
        """Handle current time."""
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            self.broadcast_link_state()
            # TODO
            #   broadcast the link state of this router to all neighbors
            pass

    def broadcast_link_state(self):
        seq, neighbors = self.lsdb[self.addr]
        content = f"{self.addr}|{seq}|{str(neighbors)}"
        packet = Packet(Packet.ROUTING, self.addr, None, content)

        for port in self.links:
            self.send(port, packet)

    def compute_forwarding_table(self):
        # Dijkstra's algorithm
        dist = {self.addr: 0}
        prev = {}
        visited = set()
        heap = [(0, self.addr)]

        graph = {}
        for node, (_, neighbors) in self.lsdb.items():
            graph[node] = neighbors

        while heap:
            cost_u, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)

            for v, cost_uv in graph.get(u, {}).items():
                if v not in dist or cost_u + cost_uv < dist[v]:
                    dist[v] = cost_u + cost_uv
                    prev[v] = u
                    heapq.heappush(heap, (dist[v], v))

        # Xây bảng chuyển tiếp từ đường đi ngắn nhất
        self.forwarding_table = {}
        for dest in dist:
            if dest == self.addr:
                continue
            # Lần ngược về để tìm next-hop
            next_hop = dest
            while prev.get(next_hop) != self.addr:
                next_hop = prev[next_hop]
            if next_hop in self.ports:
                self.forwarding_table[dest] = self.ports[next_hop]

    def __repr__(self):
        """Representation for debugging in the network visualizer."""
        # TODO
        #   NOTE This method is for your own convenience and will not be graded
        return f"LSrouter(addr={self.addr})"
