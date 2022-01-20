import socket
import json

from threading import Thread

from project.utils import *

class UdpServer(Thread):
    def __init__(self, udp_port, lock, main_server):
        Thread.__init__(self)
        self.lock = lock
        self.is_listening = True
        self.udp_port = int(udp_port)

        self.sock = None
        self.main_server = main_server

    def run(self):
        self._run_socket()
        # Принимаем сообщения
        self._handle_recv()


    def stop(self):
        self.sock.close()

    def _run_socket(self) -> None:
        """
        Запускаем серверный сокет udp
        :return:
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.udp_port))
        self.sock.setblocking(False)
        self.sock.settimeout(5)

    def _handle_recv(self) -> None:
        """
        Обрабатываем сокет клиента
        :param client_socket:
        :return:
        """
        while self.is_listening:
            try:
                data_bytes, addr = self.sock.recvfrom(1024)
                print('udp: ', data_bytes)
            except socket.timeout:
                continue
            except OSError:
                break
            if not data_bytes:
                continue
            try:
                data = bytes_to_dict(data_bytes)
                self._call_handler(data, addr)
            except KeyError as e:
                print(e)
            except ValueError as e:
                print(e)
            finally:
                pass
        self.stop()

    def _call_handler(self, data, addr):
        action = data.get('action')
        client = self.main_server.clients.get(data.get('identifier', ''))
        # handle data  here
        event = self.main_server._actions.get(action)
        if event:
            event(**data, server=self.main_server, client=client, addr=addr, socket=self.sock)
