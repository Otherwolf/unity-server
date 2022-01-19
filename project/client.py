import uuid
import json
import socket

from typing import Union


class Client:

    def __str__(self):
        return f'Client: {self.addr}'

    __repr__ = __str__

    def __init__(self, addr: tuple, udp_port: Union[str, int], socket: socket):
        self._socket = socket
        self.identifier = str(uuid.uuid4())
        self.addr = addr
        self.udp_addr = (addr[0], int(udp_port))

        self.props = {}

    def send_tcp(self, data: Union[str, dict]) -> None:
        message = json.dumps(dict(data))
        self._socket.send(str.encode(message))

    def send_udp(self, data: Union[str, dict]) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps(dict(data))
        sock.sendto(str.encode(message), self.udp_addr)
