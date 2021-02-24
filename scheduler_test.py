#!/usr/bin/env python3
from scheduler import TVisionScheduler
import utils
import time

from multiprocessing import Process

def test_socket():
    
    task_write = """
    {
        "time": "12:30",
        "verb": "write",
        "socket_name": "test.sock",
        "message": "37"
    }
    """
    p = Process(target=utils.socket_server, args=("test.sock",))
    p.daemon = True
    p.start()
    time.sleep(5)
    print("starting scheduler for writing...")
    sched = TVisionScheduler(task_write)
    sched.run()
    
def test_start_stop():

    task_start = """
    {
        "time": "11:30",
        "verb": "start",
        "program_name": "/usr/bin/gedit",
        "pidfile_name": "test_1.pid"
    }
    """

    task_stop = """
    {
        "time": "11:30",
        "verb": "stop",
        "pidfile_name": "test_1.pid"
    }
    """

    sched1 = TVisionScheduler(task_start)
    sched1.run()
    
    time.sleep(5)
    
    sched2 = TVisionScheduler(task_stop)
    sched2.run()

if __name__ == "__main__":

    #test_socket()
    test_start_stop()