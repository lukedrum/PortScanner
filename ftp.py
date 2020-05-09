import socket
import re

_ftp_response_regex = re.compile('^([0-9]+) (.+)$')

TEST_VECTOR = [b'NOOP\n', b'SYST\n', b'LIST\n']

DEFAULT_PORT = 21

RESP_LEN = 256

class FtpConn:
    def __init__(self, s):
        self._s = s
        s.settimeout(2)
        try:
            greet_resp = s.recv(RESP_LEN).decode('ascii').strip()
            greet_resp_match = _ftp_resp_split(greet_resp)
        except socket.timeout:
            print('FTP ERROR: No greeting, possibly not ftp')
            self._is_ftp = False
            return

        if not greet_resp_match:
            print('FTP ERROR: Bad greet: "' + greet_resp + '"')
            self._is_ftp = False
            return

        (code, msg) = greet_resp_match

        if code >= 300:
            print('FTP WARN: Greeting returned bad code: "' + greet_resp + '"')

        for test in TEST_VECTOR:
            s.send(test)
            resp = s.recv(RESP_LEN).decode('ascii').strip()

            m = re.match(_ftp_response_regex, resp)

            # if any test vector fails, its not real ftp
            if not m:
                self._is_ftp = False
                return
        
        self._is_ftp = True
        self._greet = msg

    def get_version_string(self):
        resp = _ftp_run_cmd(self._s, 'SYST')
        (code, msg) = _ftp_resp_split(resp)

        # if server doesn't let us SYST without logging in
        # return greeting as version string, otherwise return both greeting and SYST response
        if code >= 300:
            return self._greet
        else:
            return self._greet + ' | ' + msg

    def is_valid(self):
        return self._is_ftp

def _ftp_resp_split(resp):
    m = re.match(_ftp_response_regex, resp)

    if not m:
        return None

    code = int(m.group(1))
    msg = m.group(2)

    return (code, msg)

def _ftp_run_cmd(s, cmd):
    if not (cmd.endswith('\n') or cmd.endswith('\r\n')):
        cmd += '\n'
    
    cmd = cmd.encode('ascii')
    s.send(cmd)

    resp = s.recv(RESP_LEN)
    resp = resp.decode('ascii').strip()

    return resp

