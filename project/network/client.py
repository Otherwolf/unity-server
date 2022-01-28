import uuid

from typing import Tuple

from project.network.protocol import TCPServer, Packet

class Client:

    def __str__(self):
        return f'Client: {self.identifier}'

    __repr__ = __str__

    def __init__(self):
        self._socket = None
        self._udp_socket = None
        self.identifier = str(uuid.uuid4())
        self.udp_addr = None

        self.props = {}

    def init_udp(self, udp_addr: Tuple[str, int], udp_socket: TCPServer):
        self._udp_socket = udp_socket
        self.udp_addr = udp_addr
        return self

    def init_tcp(self, tcp_socket: TCPServer):
        self._socket = tcp_socket
        return self

    def send_tcp(self, data: Packet) -> None:
        message = data.json()
        self._socket.transport.write(str.encode(message))

    def send_udp(self, data: Packet) -> None:
        message = data.json()
        self._udp_socket.transport.write(str.encode(message), self.udp_addr)
