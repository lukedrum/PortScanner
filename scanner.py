# builtins
import argparse
import threading
import queue
import socket

# custom modules
import internals.specparser as specparser
import internals.services as serv

def is_port_open(host, port):
    s = socket.socket()

    try:
        s.settimeout(1)
        s.connect((host, port))
    except:
        return False
    else:
        return True

def worker_code(worker_id, task_q, result_q, services, port_map):
    while True:
        task = task_q.get()

        if not task: # stop on 'None' tasks
            break

        (host, port) = task

        status = is_port_open(host, port)

        if not status:
            result_q.put((host, port, 'closed', None, None))
            continue
        
        (service, info_string) = serv.identify(host, port, services, port_map)

        result_q.put((host, port, 'open', service, info_string))
    return True

# context for global variables describing the scan
if __name__ == "__main__":
    scanner_context = {}

    # argparsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", help="Print debug statements", action="store_true")
    parser.set_defaults(debug=False)
    parser.add_argument("-p", "--ports", type=str, help="String describing a set of numbers", default="1-1000")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads", default=1)
    parser.add_argument("-a", "--address", type=str, dest="addresses", action="append",
                        help="IP host or network address of a target (can be specified multiple times)")
    parser.add_argument("-A", "--addrfile", type=str, dest="addrfiles", action="append",
                        help="Name of a file which holds IP host or network addresses (can be specified multiple times)")
    args = parser.parse_args()

    scanner_context["ports"] = specparser.number_set(args.ports)
    scanner_context["addresses"] = specparser.address_set(args.addresses, args.addrfiles)
    scanner_context["threads"] = args.threads
    scanner_context["debug"] = args.debug

    scanner_context["services"] = serv.load(debug=scanner_context["debug"])
    scanner_context["port_map"] = serv.map_ports(scanner_context["services"], debug=scanner_context["debug"])
    
    # tasks are tuples of (addr, port)
    tasks = [(addr, port) for addr in scanner_context["addresses"] for port in scanner_context["ports"]]

    # create queues for inter thread communication
    task_q = queue.Queue()
    result_q = queue.Queue()

    # fill tasks queue with tasks
    for task in tasks:
        task_q.put(task)

    for i in range(scanner_context["threads"]):
        task_q.put(None)  # dummy tasks to finish workers

    worker_pool = [ threading.Thread(target=worker_code, args=(id, task_q, result_q, scanner_context["services"], scanner_context["port_map"])) for id in range(0, scanner_context["threads"]) ]

    for worker in worker_pool:  # start the workers
        worker.start()

    for worker in worker_pool:  # wait for workers to finish
        worker.join()  # cleanup
    
    results = {}

    while not result_q.empty():
        (host, port, status, service, info_string) = result_q.get()

        if not host in results:
            results[host] = {}

        results[host][port] = (status, service, info_string)

    for host in results:
        print('Results for host "' + host + '"')

        for port in results[host]:
            (status, service, info_string) = results[host][port]

            service = service or '<unknown>'
            info_string = info_string or '<unknown>'

            print(str(port) + ': ' + status + ' - ' + service)
            print('\tINFO STRING: ' + info_string)

