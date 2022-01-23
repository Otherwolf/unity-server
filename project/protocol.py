import pydantic

from twisted.internet import protocol
from twisted.internet.protocol import ServerFactory as sf, IAddress, connectionDone, failure
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import threads
from typing import Optional, Dict, Union


class Packet(pydantic.BaseModel):
    identifier: str
    action: str
    payload: Union[dict, str, int, float]


class TCPServer(protocol.Protocol):
    main_server = None

    def connectionMade(self) -> None:
        ip = self.transport.getPeer().host
        print(f'New tcp connection from {ip}')

    def dataReceived(self, data: bytes) -> None:
        try:
            data = Packet.parse_raw(data.decode('utf-8'))
        except pydantic.error_wrappers.ValidationError:
            print('received not valid tcp-data: ', data)
            return
        self.main_server.handle_incoming_package(data, self)
        # self.transport.loseConnection()

    def connectionLost(self, reason: failure.Failure = connectionDone):
        print('Connection lost with client')
        print(reason)
        self.main_server.handle_lost_connection(self)


class TCPFactory(sf):

    def buildProtocol(self, addr: IAddress) -> Optional[protocol.Protocol]:
        return TCPServer()


class UDPServer(DatagramProtocol):
    main_server = None

    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)

    '''
        address: (host, port)
    '''
    def datagramReceived(self, datagram: bytes, address):
        print(f"Datagram {repr(datagram)} received from {repr(address)}")

        if datagram == b"Client: Ping" or datagram == "Client: Ping":
            # Rather than replying to the group multicast address, we send the
            # reply directly (unicast) to the originating port:
            self.transport.write(b"Server: Pong", address)
        try:
            data = Packet.parse_raw(datagram.decode('utf-8'))
        except pydantic.error_wrappers.ValidationError:
            print('received not valid udp-data: ', datagram)
            return
        threads.deferToThread(self.main_server.handle_incoming_package, data, self, address)
