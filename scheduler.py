#!/usr/bin/env python3
import sys
try:
    import psutil
except ImportError:
    print("WARNING: NO module psutil - please run 'pip install psutil' ")
    sys.exit(-1)
try:
    import schedule
except ImportError:
    print("WARNING: NO module schedule - please run 'pip install psutil' ")
    sys.exit(-1)

import dateutil.parser
from datetime import datetime
import json
import os
from os import path
import subprocess
from subprocess import Popen
import ntpath
import time
import socket
import sched
import threading
import schedule
# from threading import Timer

class TVisionScheduler():
   
    def __init__(self, json_task):
        self.task_details = {}
        self.json_task = json_task
        self.current_pid = 0
        self.pid_from_file = 0
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.actions={
            'start':self.__startProcess,
            'stop':self.__stopProcess,
            'write':self.__writeProcess
            }
        self.stop_event = threading.Event() 
    
    def stopAll(self):
        print("Stopping all!")
        self.stop_event.set()

    def run(self):
        try:
            if path.exists(self.json_task):
                with open(self.json_task, "r") as json_file:
                    self.task_details = json.load(json_file)
            else:
                self.task_details = json.loads(self.json_task)
        except ValueError as err:
            print(f"ERROR loading JSON config {err}")

        task_action = self.task_details["verb"]
        execution_time = self.task_details["time"]
        schedule.every().day.at(execution_time).do(self.actions[task_action])
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def __isProcessRunningByName(self) -> bool:
        for proc in psutil.process_iter():
            try:
                program_name = ntpath.basename(self.task_details["program_name"]).lower()
                if program_name in proc.name().lower():
                    self.current_pid = proc.pid
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def __isProcessRunningByPID(self) -> bool:
        return psutil.pid_exists(int(self.pid_from_file))

    def __readPIDFile(self) -> bool:
        retVal = False
        try:
            with open(self.task_details["pidfile_name"], "r") as pidfile:
                self.pid_from_file = pidfile.readline()
                retVal = True
        except IOError:
            print ("PID file not accessible")
        return retVal

    def __updatePIDFile(self):
        pid_filename = self.task_details["pidfile_name"]
        if path.exists(pid_filename):
            os.remove(pid_filename)
        with open(pid_filename, "w+") as pidfile:
            pid = pidfile.write(str(self.current_pid))
            print("PID updated!")

    def __startProcess(self):
        program_name = self.task_details['program_name']
        if(self.__isProcessRunningByName()):
            if self.__readPIDFile():
                if str(self.current_pid) == str(self.pid_from_file):
                    print(f"Process {program_name} is running")
                else:
                    self.__updatePIDFile()
            else:
                print("PID File does not exist, creating it...")
                self.__updatePIDFile()
        else:
            try:
                subprocess.Popen([program_name])
                #validate the process is running and update pid file
                if(self.__isProcessRunningByName()):
                    self.__updatePIDFile()
                else:
                    print("ERROR - the given process is not running...")
            except Exception as err:
                print (f"Failed to start program: {err}")

    def __stopProcess(self):
        if self.__readPIDFile():
            if(self.__isProcessRunningByPID()):
                #TODO: check  matching PID
                for proc in psutil.process_iter():
                    try:
                        if proc.pid == int(self.pid_from_file):
                            proc.terminate()
                            os.remove(self.task_details['pidfile_name'])
                            print('Process has been stopped successfully')
                    except Exception as err:
                        print(f"Failed to kill process {self.task_details['program_name']} - err: {err}")
                        pass
            else:
                print(f"ERROR: Process with PID {self.pid_from_file} is NOT running")
                os.remove(self.task_details['pidfile_name'])

    def __writeProcess(self):
        socket_name = self.task_details["socket_name"]
        message = self.task_details["message"]
        if os.path.exists(socket_name):
            try:
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(socket_name)
                client.send(message.encode('utf-8'))
                print("message sent..")
            except Exception as err:
                print(f"ERROR connecting to socket - {err}")
        else:
            print("ERROR - Socket does NOT exist")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        tv_sched = TVisionScheduler(sys.argv[1])
        try:
            tv_sched.run() 
        except (KeyboardInterrupt, SystemExit):
            tv_sched.stopAll()
            sys.exit()       
    else:
        print("INVALID USAGE! Please specify the file name")