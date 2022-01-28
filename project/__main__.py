import argparse

from project.fps_extension import FPSExtension

parser = argparse.ArgumentParser()

parser.add_argument(
    "--tcpport", dest="tcp_port", help="Listening tcp port", default="8001"
)
parser.add_argument(
    "--udpport", dest="udp_port", help="Listening udp port", default="8002"
)

args = parser.parse_args()

if __name__ == "__main__":
    game = FPSExtension(args.tcp_port, args.udp_port)
    game.run_server()
