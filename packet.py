import copy


class Packet:
    """
    The Packet class defines packets that clients and routers send in the simulated -
    network. - Lớp Packet định nghĩa các gói tin mà các client và router gửi trong mạng được mô phỏng.

    Parameters - Các tham số
    ----------
    kind
        Either Packet.TRACEROUTE or Packet.ROUTING. Use Packet.ROUTING for all packets 
        - Hoặc là Packet.TRACEROUTE  hoặc Packet.ROUTING. Sử dụng Packet.ROUNTING cho tất cả các gói tin được tạo bởi các cài đặt của bạn
        created by your implementations.
    src_addr
        The address of the source of the packet. - Địa chỉ nguồn của gói tin
    dst_addr
        The address of the destination of the packet. - Địa chỉ đích của gói tin
    content
        The content of the packet. Must be a string. - Nội dung của gói tin . Phải là 1 xâu ký tự
    """

    TRACEROUTE = 1
    ROUTING = 2

    """Hàm khởi tạo"""

    def __init__(self, kind, src_addr, dst_addr, content=None):
        self.kind = kind
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.content = content
        self.route = [src_addr]

    def copy(self):
        """Create a deep copy of the packet.

        This gets called automatically when the packet is sent to avoid aliasing issues.

        Trả về một bản sao độc lập hoàn toàn (deep copy) của gói tin để tránh các lỗi khi nhiều router dùng chung dữ liệu gói tin.

        """
        content = copy.deepcopy(self.content)
        p = Packet(self.kind, self.src_addr, self.dst_addr, content=content)
        p.route = list(self.route)
        return p

    @property
    def is_traceroute(self):
        """Returns True if the packet is a traceroute packet."""
        return self.kind == Packet.TRACEROUTE

    @property
    def is_routing(self):
        """Returns True is the packet is a routing packet."""
        return self.kind == Packet.ROUTING

    """Thêm một địa chỉ (router trung gian) vào danh sách tuyến đường (self.route) của gói tin. """

    def add_to_route(self, addr):
        """DO NOT CALL from DVrouter or LSrouter!"""
        self.route.append(addr)

    """Nếu lớp Packet có thuộc tính animate thì gọi hàm đó để hiển thị hình ảnh mô phỏng gửi gói tin từ src đến dst với độ trễ latency."""

    def animate_send(self, src, dst, latency):
        """DO NOT CALL from DVrouter or LSrouter!"""
        if hasattr(Packet, "animate"):
            Packet.animate(self, src, dst, latency)
