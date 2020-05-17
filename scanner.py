# builtins
import argparse
import threading
import queue  # for exception Empty
import time
import socket

# custom modules
import specparser

# context for global variables describing the scan
if __name__ == "__main__":
    scanner_context = {}

    # argparsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--ports", type=str, help="String describing a set of numbers", default="440-450")
    parser.add_argument("-t", "--threads", type=int, help="Number of threads", default=1)
    parser.add_argument("-a", "--address", type=str, dest="addresses", action="append",
                        help="IP host or network address of a target (can be specified multiple times)")
    parser.add_argument("-A", "--addrfile", type=str, dest="addrfiles", action="append",
                        help="Name of a file which holds IP host or network addresses (can be specified multiple times)")
    args = parser.parse_args()

    scanner_context["ports"] = specparser.number_set(args.ports)
    scanner_context["threads"] = args.threads
    scanner_context["addresses"] = args.addresses
    print(type(scanner_context["addresses"]))

    for ind, addr_name in enumerate(args.addrfiles):
        with open(addr_name) as addres_file:
            new_addr = [line.rstrip('\n') for line in addres_file]

    if scanner_context["addresses"] is not None:
        for ind, single_addr in enumerate(new_addr):
            if single_addr not in scanner_context["addresses"]:
                scanner_context["addresses"].append(single_addr)
    else:
        scanner_context["addresses"] = new_addr

    print(scanner_context["addresses"])
    # tasks are tuples of (addr, port)
    tasks = [(addr, port) for addr in scanner_context["addresses"] for port in scanner_context["ports"]]

    # create queues for IPC
    task_q = queue.Queue()
    result_q = queue.Queue()


    # fill tasks queue with tasks
    for task in tasks:
        task_q.put(task)

    for i in range(scanner_context["threads"]):
        task_q.put(None)  # dummy tasks to finish workers


    def is_port_open(host, port):
        s = socket.socket()

        try:
            s.connect((host, port))
            s.settimeout(0.2)
        except:
            return False
        else:
            return True

    # worker code
    def worker(worker_id, task_q, result_q):
        while True:
            task = task_q.get()

            if not task:
                break
            status = is_port_open(task[0], task[1])
            print(str(worker_id) + " simulating work on a task" + str(task))
            # time.sleep(1)

            result_q.put(("result from", task, status))

        return True


    worker_pool = [threading.Thread(target=worker, args=(id, task_q, result_q)) for id in range(0, scanner_context["threads"])]

    start_time = time.time()
    for worker in worker_pool:  # start the workers
        worker.start()

    for worker in worker_pool:  # wait for workers to finish
        worker.join()  # cleanup

    print(time.time()-start_time)

    results = list()
    while not result_q.empty():
        results.append(result_q.get())

    # print(results)
