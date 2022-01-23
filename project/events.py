import json

from project.protocol import Packet


def handle_position(server, data: Packet, client, **kwargs) -> None:
    if client and data:
        server.set_udp_message(data)
        server.send_to_all_udp()
