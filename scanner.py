# builtins
import argparse
import queue  # for exception Empty
import time
import socket

# custom modules
from multiprocessing import Queue, Process
from threading import Thread

from pathos.multiprocessing import ProcessingPool as Pool

import dill

import specparser

# context for global variables describing the scan

scanner_context = {}

# argparsing
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--ports", type=str, help="String describing a set of numbers", default="440-450")
parser.add_argument("-t", "--threads", type=int, help="Number of threads", default=10)
parser.add_argument("-a", "--address", type=str, dest="addresses", action="append",
                    help="IP host or network address of a target (can be specified multiple times)")
parser.add_argument("-A", "--addrfile", type=str, dest="addrfiles", action="append",
                    help="Name of a file which holds IP host or network addresses (can be specified multiple times)")
args = parser.parse_args()

scanner_context["ports"] = specparser.number_set(args.ports)
scanner_context["threads"] = args.threads
scanner_context["addresses"] = args.addresses

# tasks are tuples of (addr, port)
tasks = [(addr, port) for addr in scanner_context["addresses"] for port in scanner_context["ports"]]

# create queues for IPC
task_q = Queue()
result_q = Queue()

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
        if task is not None:

            status = is_port_open(task[0], task[1])
            result_q.put(("result from", task, status))
            # print(task, status)
            time.sleep(2)
        if not task:
            break


if __name__ == "__main__":

    worker_pool = []
    for id in range(0, scanner_context["threads"]):
        process = Process(target=worker(id, task_q, result_q), args=(id, task_q, result_q))
        worker_pool.append(process)

    for worker in worker_pool:  # start the workers
        worker.start()

    for worker in worker_pool:  # wait for workers to finish
        worker.join()  # cleanup

    results = list()
    while not result_q.empty():
        results.append(result_q.get())

    for ind, val in enumerate(results):
        if val[2]:
            print(results[ind])
