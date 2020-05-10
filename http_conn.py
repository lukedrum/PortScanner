import socket


def http_conn():
    target_host = "target host"

    target_port = "target port"  
    
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((target_host, target_port))

    # send some data
    request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host
    client.send(request.encode())

    # receive some data
    response = client.recv(4096)

    # display the response
    print(response)


if __name__ == "__main__":
    http_conn()
