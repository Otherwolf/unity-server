import uuid
import json
import socket

from typing import Union, Tuple


class Client:

    def __str__(self):
        return f'Client: {self.identifier} /{self.udp_addr}'

    __repr__ = __str__

    def __init__(self):
        self._socket = None
        self._udp_socket = None
        self.identifier = str(uuid.uuid4())
        self.addr = None
        self.udp_addr = None

        self.props = {}

    def init_udp(self, udp_addr: Tuple[str, int], udp_socket: socket):
        self._udp_socket = udp_socket
        self.udp_addr = udp_addr
        return self

    def init_tcp(self, tcp_addr: Tuple[str, int], tcp_socket: socket):
        self._socket = tcp_socket
        self.addr = tcp_addr
        return self

    def send_tcp(self, data: Union[str, dict]) -> None:
        message = json.dumps(dict(data))
        self._socket.send(str.encode(message))

    def send_udp(self, data: Union[str, dict]) -> None:
        message = json.dumps(dict(data))
        self._udp_socket.sendto(str.encode(message), self.udp_addr)

    def close(self) -> None:
        self._socket.close()
