import re
import socket

_http_server_regex = re.compile('^(Server:.*)', re.MULTILINE)
_http_pow_regex = re.compile('^(X-Powered-By:.*)', re.MULTILINE)

SERVICE_DESC = {
    'name': 'http',
    'default_ports': [ 80 ],
    'default_ports_ssl': [ 443 ]
}

_RESP_LEN = 256


class ConnChecker:
    def __init__(self, s):
        self._s = s
        s.settimeout(2)
        target_host, target_port = self._s.getpeername()
        test_cmd = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host
        try:
            self._resp = _http_run_cmd(self._s, test_cmd)

            self._is_http = True

        except socket.timeout:
            print('HTTP ERROR: No response, not http')
            self._is_http = False
            return

    def get_info_string(self):
        info_string =_http_resp_split(self._resp)
        return info_string

    def is_valid(self):
        return self._is_http


def _http_resp_split(resp):
    m_serv = re.search(_http_server_regex, resp)
    m_add = re.search(_http_pow_regex, resp)

    if not m_serv:
        return ""

    server = str(m_serv.group(1))
    if m_add:
        additional_server_info = str(m_add.group(1))
        info = server.strip() +" "+ additional_server_info.strip()
        return info
    else:
        return server.strip()


def _http_run_cmd(s, cmd):

    cmd = cmd.encode()
    s.send(cmd)

    resp = s.recv(_RESP_LEN)
    resp = resp.decode('ascii').strip()

    return resp
