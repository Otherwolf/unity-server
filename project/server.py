from typing import Union, Tuple
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from project.client import Client
from project.protocol import TCPFactory, Packet, TCPServer, UDPServer
from project import events


class Event(list):
    def __call__(self, *args, **kwargs):
        for listener in self:
            listener(*args, **kwargs)


class Server:
    def __init__(self, tcp_port: str, udp_port: str):
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.users = {}
        self._udp_messages = []
        self._actions = {}

    def start(self):
        """
        start udp and tcp server threads
        """
        self._init_events()

        TCPServer.main_server = self
        UDPServer.main_server = self

        # Запускаем tcp server
        endpoint = TCP4ServerEndpoint(reactor, int(self.tcp_port))
        endpoint.listen(TCPFactory())
        # Запускам udp сервер
        reactor.listenMulticast(int(self.udp_port), UDPServer(), listenMultiple=True)
        reactor.run()

        # is_running = True

        # print("Game Server.")
        # print(f"TCP {self.tcp_port} port; UDP {self.udp_port} port")
        # print("--------------------------------------")
        # print("list : list connected users")
        # print("user #user_id : print user information")
        # print("quit : quit server")
        # print("--------------------------------------")
        #
        # while is_running:
        #     cmd = input("> ")
        #     if cmd == "list":
        #         print(self.clients)
        #     elif cmd == "quit":
        #         reactor.stop()
        #         print("Shutting down server...")
        #         is_running = False

    def handle_incoming_package(self, data: Packet, client, address=None):
        event = self._actions.get(data.action)
        if event:
            event(data=data, client_socket=client, server=self, client=self.users.get(data.identifier), address=address)

    def send_to_all_tcp(self, action: str, message: Union[dict, str]) -> None:
        # Отправляем сообщениие tcp всем клиентам
        data = dict(action=action, payload=message)
        for identifier, client in self.users.items():
            client.send_tcp(data)

    def send_to(self, data: Packet, protocol=TCPServer):
        client = self.users[data.identifier]
        if protocol is TCPServer:
            client.send_tcp(data)
        else:
            client.send_udp(data)

    def send_to_all_udp(self) -> None:
        # Отправляем сообщениие udp всем клиентам
        for message in self._udp_messages:
            for identifier, client in self.users.items():
                client.send_udp(message)
        self._udp_messages = []

    def set_udp_message(self, packet: Packet) -> None:
        # добавляем в очередь новое udp сообщение
        self._udp_messages.append(packet)
    #
    def on(self, action: str, func) -> None:
        """
        Добавляем листенер на экшен рекв
        :param action:
        :param func:
        :return:
        """
        # Инициализируем ивент для событий которых нет ещё в списке
        if not self._actions.get(action):
            self._actions[action] = Event()
        self._actions[action].append(func)

    def _broadcast_init_client(self, *args, **kwargs) -> None:
        """
            Сообщаем клиентам новый актуальный список клиентов.
            Требуется поменять на событие о присоединении нового клиента или дисконнект
        :param args:
        :param kwargs:
        :return:
        """
        # broadcast
        message = {"client-list": list(self.users.keys())}
        packet = Packet(**dict(action='CLIENTS-LIST', payload=message, identifier=''))
        self.set_udp_message(packet)
        self.send_to_all_udp()

    def handle_lost_connection(self, socket):
        for user in self.users.values():
            if user._socket == socket:
                del self.users[user.identifier]
                break

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
            self.users.get(data.identifier).init_udp(address, client_socket)
            self._broadcast_init_client()

    # def get_client_by_upd_address(self, addr: Tuple[str, int]) -> Client:
    #     """
    #     Получаем клиента по udp адресу
    #     :param addr:
    #     :return:
    #     """
    #     for client in self.clients.values():
    #         if client.udp_addr == addr:
    #             return client
    #
    # def _handle_client_left(self, *args, identifier, **kwargs):
    #     """
    #    Дисконнект клиента. Закрываем всё и рассылаем инфу клиентам
    #    :param addr:
    #    :return:
    #    """
    #     if identifier:
    #         self.clients.get(identifier).close()
    #         del self.clients[identifier]
    #         self.set_udp_message('ON_LEFT_CLIENT', identifier)
    #         self.send_to_all_udp()
    #
    def _init_events(self) -> None:
        """
        Инициализируем события взаимодействия с клиентом
        :return:
        """
        # Событие на регистрацию клиента
        self.on('REGISTER', self._handle_register)
        # # Событие на перемещение игрока
        self.on('POSITION', events.handle_position)
        # # СОбытие на дисконнект клиента
        # self.on('ON_LEFT_CLIENT', self._handle_client_left)
