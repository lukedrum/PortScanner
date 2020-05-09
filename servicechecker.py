import socket
import re

import ftp

HOST = 'testip'
PORT = ftp.DEFAULT_PORT
RESP_LEN = ftp.RESP_LEN

if __name__ == '__main__':
    s = socket.socket()
    s.connect((HOST, PORT))

    ftp_conn = ftp.FtpConn(s)

    if not ftp_conn.is_valid():
        print("IS NOT FTP")
    else:
        print('IS FTP')
        print('Version string: "' + ftp_conn.get_version_string() + '"')
    


