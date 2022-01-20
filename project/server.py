from threading import Lock
from typing import Union

from project.client import Client
from project.tcp_server import TcpServer
from project.udp_server import UdpServer
from project import events


class Event(list):
    def __call__(self, *args, **kwargs):
        for listener in self:
            listener(*args, **kwargs)


class Server:
    def __init__(self, tcp_port, udp_port):
        self.tcp_port = tcp_port
        self.udp_port = udp_port

        self.clients = {}
        self._udp_messages = []
        self._actions = {}

    def start(self):
        """
        start udp and tcp server threads
        """
        lock = Lock()
        udp_server = UdpServer(self.udp_port, lock, self)
        tcp_server = TcpServer(self.tcp_port, lock, self)
        # Добавляем листенер на событие регистрации клиента
        self._init_events()

        udp_server.start()
        tcp_server.start()

        is_running = True

        print("Game Server.")
        print(f"TCP {self.tcp_port} port; UDP {self.udp_port} port")
        print("--------------------------------------")
        print("list : list connected users")
        print("user #user_id : print user information")
        print("quit : quit server")
        print("--------------------------------------")

        while is_running:
            cmd = input("> ")
            if cmd == "list":
                print(self.clients)
            elif cmd == "quit":
                print("Shutting down server...")
                udp_server.is_listening = False
                tcp_server.is_listening = False
                udp_server.stop()
                tcp_server.stop()
                is_running = False

        udp_server.join()
        tcp_server.join()

    def send_to_all_tcp(self, action: str, message: Union[dict, str]) -> None:
        data = dict(action=action, payload=message)
        for identifier, client in self.clients.items():
            client.send_tcp(data)

    def send_to_all_udp(self) -> None:
        for message in self._udp_messages:
            for identifier, client in self.clients.items():
                client.send_udp(message)
        self._udp_messages = []

    def send_to_client_tcp(self, action: str, client: Client, message: Union[dict, str]) -> None:
        data = dict(action=action, payload=message)
        client.send_tcp(data)

    def send_to_client_udp(self, action: str, client: Client, message: Union[dict, str]) -> None:
        data = dict(action=action, payload=message)
        client.send_udp(data)

    def set_udp_message(self, action: str, message: Union[dict, str]) -> None:
        self._udp_messages.append(dict(action=action, payload=message))

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

    def _broadcast_init_client(self, *args, **kwargs):
        # broadcast
        message = {
            "client-list": list(self.clients.keys())
        }
        self.set_udp_message('CLIENTS-LIST', message)
        self.send_to_all_udp()

    def _handle_register_tcp(self, identifier, client_socket, **kwargs) -> None:
        """
        Запоминаем клиента
        :param addr:
        :param payload:
        :return: Client
        """
        client = self.clients.get(identifier)
        if client:
            client.init_tcp(client_socket.getpeername(), client_socket)
            self.send_to_client_tcp("REGISTER-SUCCESS", client, {"identifier": client.identifier})
            self._broadcast_init_client()

    def _handle_register_udp(self, *args, addr, socket, **kwargs):
        client = self.get_client_by_upd_address(addr)
        if not client:
            client = Client().init_udp(addr, socket)
            self.clients[client.identifier] = client
            self.send_to_client_udp("REGISTER-SUCCESS", client, {"identifier": client.identifier})


    def get_client_by_upd_address(self, addr: tuple[str, int]) -> Client:
        for client in self.clients:
            if client.udp_addr == addr:
                return client

    def _init_events(self):
        # Событие на регистрацию udp клиента
        self.on('REGISTER_UDP', self._handle_register_udp)
        # Событие на перемещение игрока
        self.on('POSITION', events.handle_position)
        # Событие на регистрацию tcp клиента
        self.on('REGISTER_TCP', self._handle_register_tcp)
