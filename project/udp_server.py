from threading import Thread
import socket
import json


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


            #     identifier = data.get("identifier")
            #     payload = data.get("payload")
            #     action = data.get("action")
            #
                # try:
            #         self.lock.acquire()
            #
            #         if action == "update":
            #             client = self.main_server.clients[identifier]
            #
            #             for action in payload:
            #                 if action[0] == "move":
            #                     client.props["x"] = (
            #                         client.props.get("x", 0) + action[1][0]
            #                     )
            #                     client.props["y"] = (
            #                         client.props.get("y", 0) + action[1][0]
            #                     )
            #             self.main_server.udp_messages.append(
            #                 {"identifier": identifier, "message": payload}
            #             )
            #
            #         self.send_messages()
            #     finally:
            #         self.lock.release()
            # except KeyError:
            #     print('KeyError')
            #     # print(f"JSON from {addr}:{addr} is not valid")
            # except ValueError:
            #     print('ValueError')
            #     # print(f"Message from {addr}:{addr} is not valid json string")

        # self.stop()

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
                data = self._handle_bytes(data_bytes)
                self._call_handler(data, addr)
            except KeyError as e:
                print(e)
            except ValueError as e:
                print(e)
            finally:
                pass
        self.stop()

    def _get_client(self, identifier: str):
        for client in self.main_server.clients.values():
            if client.identifier == identifier:
                return client

    def _handle_bytes(self, data):
        decoded_data = data.decode('utf-8')
        return json.loads(decoded_data)

    def _call_handler(self, data, addr):
        identifier = data.get('identifier', '')
        action = data.get('action')
        client = self._get_client(identifier)
        # handle data  here
        event = self.main_server._actions.get(action)
        if event:
            event(**data, server=self.main_server, client=client, addr=addr)
