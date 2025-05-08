import time
import queue


class Router:
    """
    The Router base class that handles the details of packet send/receive and link
    changes. Subclasses should override the following methods to implement routing
    algorithm functionalities:

    Lớp Router quản lý các liên kết đến các thiết bị khác, nhận và gửi gói tin, đồng thời cung cấp các hàm cần ghi đè để bạn có thể tự triển khai thuật toán định tuyến của riêng mình.

    - __init__
    - handle_packet : 	Xử lý gói tin đến. Mặc định là gửi ngược lại như boomerang.
    - handle_new_link : 	Khi có liên kết mới xuất hiện → dùng để cập nhật bảng định tuyến hoặc gửi thông báo.
    - handle_remove_link : 	Khi một liên kết bị mất. Bạn cần cập nhật lại thông tin định tuyến tương ứng.
    - handle_time : Hàm được gọi định kỳ để gửi thông tin định tuyến (VD: bản tin DV hoặc LS).
    - __repr__ (optional, for your own debugging) : Trả về chuỗi hiển thị router trên trình giả lập đồ họa.

    Parameters
    ----------
    addr
        The address of this router. : Địa chỉ của Router
    heartbeat_time
        Routing information should be sent at least once every heartbeat_time ms. : Thông tin của router nên được gửi trong ít nhất heartbeat_time
    """

    def __init__(self, addr, heartbeat_time=None):
        self.addr = addr
        self.links = {}  # Links indexed by port - Danh sách các liên kết theo port 
        self.link_changes = queue.Queue()  # Thread-safe queue for link changes - hàng đợi lưu các thay đổi liên kết (thêm/xoá)
        self.keep_running = True

    def change_link(self, change):
        """Add, remove, or change the cost of a link.

        The `change` argument is a tuple with first element being "add" or "remove".
        
        Dùng để yêu cầu router xử lý thay đổi mạng (thêm/xoá đường liên kết).


        """
        self.link_changes.put(change)

    def add_link(self, port, endpointAddr, link, cost):
        """Add new link to router.

        Thêm liên kết vào bảng links

        Gọi các hàm handle_new_link và handle_remove_link để cập nhật logic định tuyến
        """
        if port in self.links:
            self.remove_link(port)
        self.links[port] = link
        self.handle_new_link(port, endpointAddr, cost)

    def remove_link(self, port):
        """Remove link from router."""
        self.links = {p: link for p, link in self.links.items() if p != port}
        self.handle_remove_link(port)

    def run(self):
        """Main loop of router.
        Cập nhật theo thời gian (handle_time)

        Kiểm tra xem có gói tin mới đến từ mỗi port hay không → gọi handle_packet

        Xử lý các thay đổi liên kết nếu có trong hàng đợi
        """
        while self.keep_running:
            time.sleep(0.1)
            time_ms = int(round(time.time() * 1000))
            try:
                change = self.link_changes.get_nowait()
                if change[0] == "add":
                    self.add_link(*change[1:])
                elif change[0] == "remove":
                    self.remove_link(*change[1:])
            except queue.Empty:
                pass
            for port in self.links.keys():
                packet = self.links[port].recv(self.addr)
                if packet:
                    self.handle_packet(port, packet)
            self.handle_time(time_ms)

    def send(self, port, packet):
        """Send a packet out given port."""
        try:
            self.links[port].send(packet, self.addr)
        except KeyError:
            pass

    def handle_packet(self, port, packet):
        """Process incoming packet.

        Subclasses should override this method. The default implementation simply sends
        packet back out the port it arrived.

        This method is called whenever a packet arrives on port number `port`. Check
        whether the packet is a traceroute packet or a routing packet and handle it
        appropriately. Methods and fields of the packet class are defined in packet.py.

        Parameters
        ----------
        port
            The port number on which the packet arrived.
        packet
            The received packet instance.
        """
        self.send(port, packet)

    def handle_new_link(self, port, endpoint, cost):
        """Handle new link.

        Subclasses should override this method. The default implementation is empty.

        This method is called whenever a new link is added on port number `port`
        connecting to a router or client with address `endpoint` and link cost `cost`.
        You should store the argument values in a data structure to use for routing.
        If you want to send packets along this link, call `self.send(port, packet)`.

        Parameters
        ----------
        port
            The port number on which the link was added.
        endpoint
            The address of the other endpoint of the link.
        cost
            The link cost.
        """
        pass

    def handle_remove_link(self, port):
        """Handle removed link.

        Subclasses should override this method. The default implementation is empty.

        This method is called when the existing link on port number `port` is
        disconnected. You should update the data structures appropriately.

        Parameters
        ----------
        port
            The port number on which the link was removed.
        """
        pass

    def handle_time(self, time_ms):
        """Handle current time.

        Subclasses should override this method. The default implementation is empty.

        This method is called regularly for sending routing packets at regular
        intervals.
        """
        pass

    def __repr__(self):
        """Representation for debugging in the network visualizer.

        Subclasses may override this method.

        The network visualizer will call `repr` to print current router details, whose
        behavior can be controlled by this magic method. Return any string that will be
        helpful for debugging. NOTE: This method is for your own convenience and will
        not be graded.

        Trả về chuỗi hiển thị router trên trình giả lập đồ họa.
        """
        return f"Router(addr={self.addr})"
