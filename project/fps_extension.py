import json
import time

from typing import Optional

from project.network.server import Server, Packet
from project.simulation.world import World
from project.network import consts
from project.network.client import Client
from project.simulation import player, transform
from project.network.protocol import UDPServer


class FPSExtension:
    world = None
    server = None

    def __init__(self, tcp: str = '8001', udp: str = '8002'):
        self.server = Server(tcp, udp)
        self.init()

    def run_server(self):
        self.server.start()

    def get_world(self):
        return self.world

    def init(self):
        self.world = World(self)  # Creating the world model

        # Subscribing the request handlers
        # addRequestHandler("sendAnim", SendAnimHandler.class );
        self.server.add_request_handler("CONNECTED", self.spawn_me_handler)
        self.server.add_request_handler("sendTransform", self.send_transform_handler)
        # addRequestHandler("getTime", GetTimeHandler.class );
        # addRequestHandler("shot", ShotHandler.class );
        # addRequestHandler("reload", ReloadHandler.class );
        #
        self.server.add_event_handler(consts.ServerSystemActions.USER_DISCONNECT, self.on_user_gone_handler)
        self.server.add_event_handler(consts.ServerSystemActions.USER_LOGOUT, self.on_user_gone_handler)

        print("FPS extension initialized")

    def destroy(self):
        self.world = None
        print("World destroyed")

    def on_user_gone_handler(self, client: Client, **kwargs) -> None:
        self.world.user_left(client)

    def client_instantiate_player(self, player: player.Player):
        self._client_instantiate_player(player, None)

    def _client_instantiate_player(self, player: player.Player, target_user: Optional[Client]):
        packet = Packet(action="spawnPlayer", identifier=player.client.identifier, payload=player.to_packet())

        if not target_user:
            self.server.send_to_all(packet, protocol=UDPServer)
        else:
            self.server.send_to(packet, target=target_user, protocol=UDPServer)

    def spawn_me_handler(self, client, **kwargs):
        new_player = self.world.add_or_respawn_player(client)
        if new_player:
            # Send this player data about all the other players
            self.send_other_players_info(client)
        self.world.spawn_items()

    def send_other_players_info(self, user: Client) -> None:
        for player in self.world.get_players():
            if player.is_dead():
                continue
            if player.client.identifier != user.identifier:
                self._client_instantiate_player(player, user)

    def send_transform_handler(self, data: Packet, client: Client, **kwargs):
        received_transform = transform.Transform.from_packet(json.loads(data.payload))
        result = self.world.move_player(client, received_transform)
        if result:
            self.send_transform(client, result)
        else:
            packet = Packet(action="notransform", identifier=client.identifier)
            packet.payload = self.world.get_player(client).to_packet()
            self.server.send_to(packet, protocol=UDPServer)

    def send_transform(self, client, transform):
        transform.time_stamp = int(time.time() * 1000.0)
        packet = Packet(action="transform", identifier=client.identifier, payload=transform.to_packet())
        self.server.send_to_all(packet, UDPServer)
