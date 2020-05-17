import socket
import ssl

import internals.services as serv

HOST = '91.198.174.192'
PORT = 443

if __name__ == '__main__':
    services = serv.load()
    port_map = serv.map_ports(services)

    if PORT in port_map:
        for mapping in port_map[PORT]:
            service_name = mapping['service_name']
            mod = services[service_name]

            s = socket.socket()

            if mapping['ssl']:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE # liberal settings

                s = context.wrap_socket(s, server_hostname=HOST)
                service_name = service_name + '/ssl'

            s.connect((HOST, PORT))

            conn = mod.ConnChecker(s)

            if not conn.is_valid():
                print("it's not " + service_name)
            else:
                print("it's " + service_name)
                print('Info string: "' + conn.get_info_string() + '"')
    


