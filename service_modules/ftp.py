import re

_ftp_response_regex = re.compile('^([0-9]+) (.+)$')

SERVICE_DESC = {
    'name': 'ftp',
    'default_ports': [ 21 ]
}

_RESP_LEN = 256

class ConnChecker:
    def __init__(self, s):
        self._s = s
        s.settimeout(2)
        try:
            greet_resp = s.recv(_RESP_LEN).decode('ascii').strip()
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

        self._is_ftp = False

        test_cmds = ['RETR somefile.txt', 'NOOP', 'SYST', 'LIST']
        for test in test_cmds:
            resp = _ftp_run_cmd(self._s, test)

            m = re.match(_ftp_response_regex, resp)

            # if any test vector fails, its not real ftp
            if m:
                self._is_ftp = True
                break
        
        self._greet = msg

    def get_info_string(self):
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

    resp = s.recv(_RESP_LEN)
    resp = resp.decode('ascii').strip()

    return resp

