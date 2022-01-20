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

    def _handle_init_client(self, *args, **kwargs):
        # broadcast
        message = {
            "client-list": list(self.clients.keys())
        }
        self.set_udp_message('CLIENTS-LIST', message)
        self.send_to_all_udp()

    def _handle_register(self, *args, **kwargs) -> None:
        """
        Запоминаем клиента
        :param addr:
        :param payload:
        :return: Client
        """
        client_socket = kwargs.get('client_socket')
        payload = kwargs.get('payload')

        for registered_client in self.clients.values():
            ip, udp_addr = registered_client.udp_addr
            if str(udp_addr) == str(payload):
                if client_socket:
                    registered_client._socket = client_socket
                self.send_to_client_tcp("REGISTER-SUCCESS", registered_client, {"identifier": registered_client.identifier})
                self._handle_init_client()
                return
        client = Client(client_socket.getpeername(), int(payload), client_socket)

        self.clients[client.identifier] = client
        self.send_to_client_tcp("REGISTER-SUCCESS", client, {"identifier": client.identifier})
        self._handle_init_client()

    def _init_events(self):
        # Событие на регистрацию udp клиента
        self.on('REGISTER', self._handle_register)
        # Событие на перемещение игрока
        self.on('POSITION', events.handle_position)
        # Принимаем udp запрос для иницииализации доступа к бродкасту
        # self.on('INIT_CLIENT', self._handle_init_client)
