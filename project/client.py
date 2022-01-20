import uuid
import json
import socket

from typing import Union


class Client:

    def __str__(self):
        return f'Client: {self.addr}'

    __repr__ = __str__

    def __init__(self, addr: tuple):
        self._socket = None
        self.identifier = str(uuid.uuid4())
        self.addr = None
        self.udp_addr = addr

        self.props = {}

    def send_tcp(self, data: Union[str, dict]) -> None:
        message = json.dumps(dict(data))
        self._socket.send(str.encode(message))

    def send_udp(self, data: Union[str, dict]) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.dumps(dict(data))
        sock.sendto(str.encode(message), self.udp_addr)
