#!/usr/bin/env python
from flask import Flask, send_file, render_template
#from prettytable import PrettyTable
import tablib
import sys
import socket
import threading
import time
import os
import shutil
from _thread import *

app = Flask(__name__)
dataset = tablib.Dataset()

MESSAGE = "d"
STOPCOMMAND = "x"
STARTCOMMAND = "o"

#BUFFER_SIZE = 2048

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')

@app.route('/SensorStream')
def sensor_stream():
    
    dataset.csv = ""
    print("Displaying contents of sensorlog.csv")
    
    with open('sensorlog.csv') as f:
        #dataset.csv = f.read()
        b =len(f.readlines())
        z= b - 10
        f.seek(0, 0)
        for i in range(b):
            
            if(i>=z):
                dataset.csv += str(f.readline()) + '\n'
            else:
                f.readline()
        data = dataset
    return render_template('index.html', data = data)


@app.route('/download')
def download_file():
    path = "sensorlog.csv"

    return send_file(path, as_attachment=True)

@app.route('/Check')
def check():
    conn.send('c'.encode()) 
    return render_template('index.html')

@app.route('/Exit')
def exit():
    temp_results[1] = "EXIT"
    sys.exit(0) 
    return render_template('index.html')
    
@app.route('/StopSending')
def stop_sending():
    sendoff()
    #s.send(STOPCOMMAND.encode())
    return render_template('index.html')

@app.route('/ResumeSending')
def resume_sending():
    sendon()
    #s.send(STARTCOMMAND.encode())

    return render_template('index.html')

def Webserver(args):
    app.run(host='0.0.0.0', port=80)

def WebListener(conn, results):

    while(True):
        datarecv = conn.recv(BUFFER_SIZE).decode()
        if(datarecv[0]=="c"):
            print(datarecv)
            if(datarecv[2]=="o"):
                print("Client sending is on!")
            else:
                print("Client sending is off.")
            #print("STATE: "+ datarecv[2])
        elif(datarecv[0]=="s"):
            datarecv = datarecv.split()
            datarecv[0] = "" #Removing command and byte length.
            datarecv[1] = ""
            datarecv = "".join(datarecv)
            results[0] = datarecv

def sendon():
    print("Resume sending.")
    temp_results[2]=True
    conn.send('o'.encode())
    temp_results[1] = ""

    conn.send('c'.encode()) #Check

def sendoff():
    print("Stop Sending")
    temp_results[2]=False
    conn.send('x'.encode())
    temp_results[1] = ""

    conn.send('c'.encode()) #Check

if __name__ == "__main__":

    SEPARATOR = "<SEPARATOR>"

    f = open("sensorlog.csv", "w+")
    f.write('time, tempsensor, temperature, ldrValue'+'\n')

    print("Hello")

    TCP_IP = '0.0.0.0'
    TCP_PORT = 5003
    WEB_PORT = 5003
    BUFFER_SIZE = 2048  # Normally 1024

    temp_results = [0,0,0]
    result=[]
    temp_results[1] = ""

    start_new_thread(Webserver, (temp_results,))

    print("Binding...")
    s = socket.socket()
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print("Listening....")

    conn, addr = s.accept()

    print("Starting thread...")
    webListen = threading.Thread(target=WebListener,args=(conn, temp_results,))
    webListen.start()
    
    temp_results[2] = True #Determines if client is sending sampling data.

    while True:
        
        if(temp_results[1]==""):
            if(temp_results[2]):
                print('\nReceived: ' + str(temp_results[0]))
                if(temp_results[0]!=0):
                    f.write(temp_results[0]+'\n')
                    f.flush()
                time.sleep(10)
        elif(temp_results[1]=="SENDOFF"):
            sendoff()
        elif(temp_results[1]=="SENDON"):
            sendon()
        elif(temp_results[1]=="EXIT"):
            sys.exit(0) 
        #if not data: break
            
