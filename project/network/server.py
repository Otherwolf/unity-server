from typing import Union, Optional
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from project.network.client import Client
from project.network import consts
from project.network.protocol import TCPFactory, Packet, TCPServer, UDPServer


class Event(list):
    def __call__(self, *args, **kwargs):
        for listener in self:
            listener(*args, **kwargs)


class Server:
    def __init__(self, tcp_port: str, udp_port: str):
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.users = {}
        self._actions = {}
        self._system_actions = {
            consts.ServerSystemActions.USER_DISCONNECT: Event(),
            consts.ServerSystemActions.USER_LOGOUT: Event()
        }

    def start(self):
        """
        start udp and tcp server threads
        """
        # self._init_events()
        print("Game Server.")
        print(f"TCP {self.tcp_port} port; UDP {self.udp_port} port")
        print("--------------------------------------")
        self._init()

        TCPServer.handle_request_callback = self.handle_incoming_package
        TCPServer.handle_system_callback = self.handle_system_callback
        UDPServer.handle_request_callback = self.handle_incoming_package

        # Запускаем tcp server
        endpoint = TCP4ServerEndpoint(reactor, int(self.tcp_port))
        endpoint.listen(TCPFactory())
        # Запускам udp сервер
        reactor.listenMulticast(int(self.udp_port), UDPServer(), listenMultiple=True)
        reactor.run()

    def handle_incoming_package(self, data: Packet, client: Union[TCPServer, UDPServer], address=None):
        """
        Обрабаытваем все входящие пакеты
        :param data:
        :param client:
        :param address:
        :return:
        """
        event = self._actions.get(data.action)
        if event:
            event(data=data, client_socket=client, server=self, client=self.users.get(data.identifier), address=address)

    def handle_system_callback(self, action: int, connection: [TCPServer, UDPServer]) -> None:
        """
        Обрабатываем все входящие системные события
        :param action:
        :param connection:
        :return:
        """
        event = self._system_actions.get(action)
        if event:
            event(client=self.get_client_by_tcp_socket(connection))

    def get_client_by_tcp_socket(self, connection: TCPServer) -> Optional[Client]:
        for client in self.users.values():
            if client._socket == connection:
                return client

    def send_to(self, data: Packet, target=None, protocol=TCPServer):
        """
        Отправляем по заданому протоколу пакет на клиента из data.identifier
        :param data:
        :param protocol:
        :return:
        """
        if not target:
            client = self.users[data.identifier]
        else:
            client = target
        if protocol is TCPServer:
            client.send_tcp(data)
        else:
            client.send_udp(data)

    def send_to_all(self, data: Packet, protocol=TCPServer):
        for client in self.users.values():
            if protocol is TCPServer:
                client.send_tcp(data)
            else:
                client.send_udp(data)

    def add_request_handler(self, action: str, func) -> None:
        """
        Добавляем листенер на событие пакета
        :param action:
        :param func:
        :return:
        """
        # Инициализируем ивент для событий которых нет ещё в списке
        if not self._actions.get(action):
            self._actions[action] = Event()
        self._actions[action].append(func)

    def add_event_handler(self, action: int, func) -> None:
        """
        Добавляем листенер на системное событие
        :param action:
        :param func:
        :return:
        """
        self._system_actions[action].append(func)

    def handle_lost_connection(self, client: Client, **kwargs):
        if client:
            del self.users[client.identifier]
            client.close()

    def _handle_register(self, data: Packet, client_socket: Union[TCPServer, UDPServer], address, **kwargs) -> None:
        """
        Сохраняем сведения в CLient o соединении и создаём клиента если его ещё не было
        :param addr:
        :param socket:
        :param kwargs:
        :return:
        """
        if isinstance(client_socket, TCPServer):
            client = Client().init_tcp(client_socket)
            self.users[client.identifier] = client
            packet = Packet(**dict(action="REGISTER-SUCCESS", identifier=client.identifier, payload=""))
            self.send_to(packet)
        else:
            client = self.users.get(data.identifier).init_udp(address, client_socket)
            packet = Packet(**dict(action="CONNECTED", identifier=client.identifier, payload=""))
            self.handle_incoming_package(packet, client_socket, address)

    def _init(self) -> None:
        """
        Инициализируем события взаимодействия с клиентом
        :return:
        """
        # Событие на регистрацию клиента
        self.add_request_handler('REGISTER', self._handle_register)
        self.add_request_handler('ON_LEFT_CLIENT', self.handle_lost_connection)
        # Событие на потерю соединения
        self.add_event_handler(consts.ServerSystemActions.USER_DISCONNECT, self.handle_lost_connection)
        self.add_event_handler(consts.ServerSystemActions.USER_LOGOUT, self.handle_lost_connection)
