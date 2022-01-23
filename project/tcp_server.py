# import socket
# import json
#
# from threading import Thread
# from typing import Union
# from select import select
#
# from project.utils import *
#
#
# class TcpServer(Thread):
#     def __init__(self, tcp_port, lock, main_server):
#         Thread.__init__(self)
#         self.lock = lock
#         self.tcp_port = int(tcp_port)
#         self.is_listening = True
#
#         self.sock = None
#         self.main_server = main_server
#         self._connections = []
#
#     def run(self):
#         """
#         Метод запуска сервера
#         :return:
#         """
#         # Запускаем серверный сокет
#         self._run_socket()
#         # Запускаем событийный цикл
#         self._event_loop()
#
#     def stop(self) -> None:
#         """
#         Выключает сервер tcp
#         :return:
#         """
#         self.sock.close()
#
#     def send(self, data: Union[str, dict], sock: socket) -> None:
#         """
#         Отправка сообщения клиенту по tcp
#         :param data:
#         :param sock:
#         :return:
#         """
#         message = json.dumps({"message": data})
#         sock.send(str.encode(message))
#
#     def _run_socket(self) -> None:
#         """
#         Запускаем серверный сокет tcp
#         :return:
#         """
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind(("", self.tcp_port))
#         self.sock.setblocking(False)
#         self.sock.settimeout(5)
#         self.sock.listen(5)
#         self._connections.append(self.sock)
#
#     def _accept_connection(self, server_socket: socket) -> None:
#         """
#         Принимаем новый сокет
#         :return:
#         """
#         try:
#             client_socket, addr = server_socket.accept()
#             client_socket.setblocking(False)
#             print('connection from: ', addr)
#             self._connections.append(client_socket)
#         except socket.timeout:
#             pass
#
#     def _event_loop(self) -> None:
#         """
#         Основной событийный цикл
#         :return:
#         """
#         while self.is_listening:
#             ready_to_read, w, e = select(self._connections, [], [])
#
#             for sock in ready_to_read:
#                 if sock is self.sock:
#                     self._accept_connection(sock)
#                 else:
#                     self._handle_recv(sock)
#         # выключаем сервер
#         self.stop()
#
#     def _handle_recv(self, client_socket: socket) -> None:
#         """
#         Обрабатываем сокет клиента
#         :param client_socket:
#         :return:
#         """
#         while self.is_listening:
#             try:
#                 data_bytes = client_socket.recv(1024)
#             except BlockingIOError:
#                 return
#             except OSError:
#                 break
#             if not data_bytes:
#                 return
#             if data_bytes == b'close':
#                 break
#             try:
#                 data = bytes_to_dict(data_bytes)
#                 print(data)
#
#                 action = data.get('action')
#                 # handle data  here
#                 event = self.main_server._actions.get(action)
#                 if event:
#                     event(**data, client_socket=client_socket, server=self.main_server)
#             except KeyError as e:
#                 print(e)
#                 self.send("Json is not valid", client_socket)
#             except ValueError as e:
#                 print(e)
#                 self.send("Message is not a valid json string", client_socket)
#             finally:
#                 pass
#         print('close client socket')
#
#         self._connections.remove(client_socket)
#         client_socket.close()
