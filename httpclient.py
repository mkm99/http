#! /usr/bin/env python3
# Echo Client
"""
Programming language and version: Python 3.8.1
Testing Environment:
    OS: Windows
    IDE with entrance file: N/A
    Command Lines:
        python httpclient.py 127.0.0.1:12000/filename.html
"""

import sys
import socket
import os.path
import datetime

# getting the whole string argument
argInput = sys.argv[1]
# splitting to get the host
split1 = argInput.split(':')
# splitting to get the port number and the file
split2 = split1[1].split('/')

host = split1[0]
port = int(split2[0])
file = split2[1]

# check if cache.txt exists or not
exists = os.path.isfile('cache.txt')

# If it does not exist it means fileName.html has not been cached
# and cache.txt would be created
if not exists:
    # If file does not exists, then GET request will be send
    # making cache.txt
    makeFile = open("cache.txt", "w")
    makeFile.close()
    # making a string for GET request
    message = "GET /" + file + " HTTP/1.1\r\n" +\
              "Host: " + host + ":" + str(port) + "\r\n\r\n"

    # print out the GET Request
    print("\nGET Request: \n", message)

# If cache.txt exists, then "Conditional GET Request" will be send
else:
    # read the date saved in cache.txt to see what was the last time it was modified
    cacheTXT = open('cache.txt', 'r')
    cacheTimeGMT = cacheTXT.read()
    cacheTXT.close()

    # making a string for Conditional GET Request
    message = "GET /" + file + " HTTP/1.1\r\n" + \
              "Host: " + host + ":" + str(port) + "\r\n" + \
              "If-Modified-Since: " + cacheTimeGMT + "\r\n\r\n"

    # print out Conditional GET Request
    print("\nConditional GET Request: \n", message)

# Create TCP client socket. Note the use of SOCK_STREAM for TCP packet
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create TCP connection to server
clientSocket.connect((host, port))

# Send encoded data through TCP connection
clientSocket.send(message.encode())

# Receive the server response
count = 65495
dataEcho = clientSocket.recv(count)

# printing out the response from the server
print("HTTP Response:")

# Display the decoded server response as an output
print(dataEcho.decode())

# get dataEcho in a string to search for the last modification date of fileName
echoString = dataEcho.decode()


if "Last-Modified" in echoString:
    last_mod = ''

    # this block of code is check for 'Last-Modified'
    # splitting echo in lines
    echoLines = echoString.splitlines()

    for line in echoLines:
        if 'Last-Modified' in line:
            # splitting after the third line from the ':' since it will have the date/time
            last_mod = line.split(": ")
            # saving the last modification date/time
            last_mod = last_mod[1]

    if exists:
        # write in the file the modification date of fileName to check if the fileName has changed
        f = open('cache.txt', 'w')
        f.write(last_mod)
        f.close()
    else:
        nowTime = datetime.datetime.now(datetime.timezone.utc)
        nowTimeGMT = nowTime.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n")
        f = open('cache.txt', 'w')
        f.write(nowTimeGMT)
        f.close()

# Close the client socket
clientSocket.close()