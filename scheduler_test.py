#!/usr/bin/env python3
from scheduler import Scheduler
import utils
import time
import datetime
import pytest
import threading

def test_socket():
    start_time = utils.getFutureTime(datetime.datetime.now(), 1)
    socket_name="test.sock"

    task_write = f"""
    {{
        "time": "{start_time}",
        "verb": "write",
        "socket_name": "{socket_name}",
        "message": "37"
    }}
    """
    print(task_write)

    message_received_event = threading.Event()
    p = threading.Thread(target=utils.socket_server, name="SocketServer-Thd", args=(socket_name, message_received_event)).start()
    sched = Scheduler(task_write)
    t = threading.Thread(name="TestSocket-Thd", target=lambda sched: (sched.waitUntilComplete(), sched.stopAll()), args=[sched]).start()
    sched.run()
    assert message_received_event.is_set() == True
    
def test_start():
    start_time = utils.getFutureTime(datetime.datetime.now(), 1)
    task_start = f"""
    {{
        "time": "{start_time}",
        "verb": "start",
        "program_name": "./dummy",
        "pidfile_name": "test_1.pid"
    }}
    """
    print(task_start)

    sched1 = Scheduler(task_start, 30)
    t = threading.Thread(target=lambda sched: (sched.waitUntilComplete(), sched.stopAll()), args=[sched1]).start()
    sched1.run()
    assert sched1._Scheduler__isProcessRunningByName("dummy") == True

def test_stop():
    stop_time = utils.getFutureTime(datetime.datetime.now(), 1)
    pid_file = "test_1.pid"
    task_stop = f"""
    {{
        "time": "{stop_time}",
        "verb": "stop",
        "pidfile_name": "{pid_file}"
    }}
    """
    print(task_stop)

    proc_pid=""
    try:
        with open(pid_file, "r") as pidfile:
            proc_pid = pidfile.readline()
    except IOError:
        print ("PID file not accessible")  

    sched2 = Scheduler(task_stop, 30)
    t = threading.Thread(target=lambda sched: (sched.waitUntilComplete(), sched.stopAll()), args=[sched2]).start()
    sched2.run()
    assert sched2._Scheduler__isProcessRunningByPID(int(proc_pid)) == False

if __name__ == "__main__":
    #test_socket()
    test_start()
    test_stop()
