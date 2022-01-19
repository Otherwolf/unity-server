import json

def handle_position(server, payload, client, **kwargs):
    data = json.loads(payload)
    if client and payload:
        data['identifier'] = client.identifier
        server.set_udp_message('POSITION', data)
        server.send_to_all_udp()
