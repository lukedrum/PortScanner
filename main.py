import argparse
import socket
from multiprocessing import Process, Queue, JoinableQueue


parser = argparse.ArgumentParser(description='Tutaj możemy podać zwięzły opis naszego skryptu')
parser.add_argument('-p', '--numbers', help="Zakres liczb, pojedyncze liczby")
parser.add_argument('-a', '--address', help="Specyfikacja adresu lub sieci ip")
parser.add_argument('-A', '--address_file', help="Nazwa pliku z listami adresów i sieci")
parser.add_argument('-t', '--threads', help="Liczba wątków")


args = parser.parse_args()
host_address = args.address
hosts_file = args.address_file
threads = int(args.threads)
# single_port = args.numbers

hosts = []
f = open(hosts_file, "r")
for x in f:
    x = x.replace("\n", "")
    if x != host_address:
        hosts.append(x)
f.close()

hosts.append(host_address)




def is_port_open(host, port):
    s = socket.socket()
    try:
        s.connect((host, port))
        # s.settimeout(0.2)
    except:
        return False
    else:
        return True


def worker(tasks):
    while True:
        try:
            host, port = tasks.get()
            status = is_port_open(host, port)
            results.put((host, port, status))
            tasks.task_done()
        except ValueError:
            print('no ni ma')


tasks = JoinableQueue()

pairs = []
for num, host in enumerate(hosts):
    for port in range(1, 20):
        pairs.append((host, port))

for pair in pairs:
    tasks.put(pair)


results = Queue()


if __name__ == '__main__':

    procs = [Process(target=worker, args=(tasks,)) for _ in range(threads)]

    for p in procs:
        p.start()
        
    for p in procs:
        p.join()

