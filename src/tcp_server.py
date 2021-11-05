#!/usr/bin/env python 
import socket
import threading
import sys
import time

def temp_sensor(results):
    while(True):
        data = conn.recv(BUFFER_SIZE).decode()
        conn.flush()
        time.sleep(10)
        results[0] = data
    
if __name__ == "__main__":

    print("Hello")

    TCP_IP = '192.168.43.209'
    TCP_PORT = 1234
    BUFFER_SIZE = 2048  # Normally 1024, but we want fast response

    print("Binding...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)
    print("Success!")

    conn, addr = s.accept()

    temp_results = [0,0]

    print("Starting thread...")
    temp = threading.Thread(target=temp_sensor,args=(temp_results,))
    temp.daemon = True

    temp.start()

    print ('Connection address:', addr)

    with conn:
        while True:
            print('\nReceived: ' + str(temp_results[0]))
            time.sleep(10)
            #if not data: break
            
