#! /usr/bin/env python3
# Echo Client
"""
Programming language and version: Python 3.8.1
Testing Environment:
    OS: Windows
    IDE with entrance file: N/A
    Command Lines:
        python httpserver.py 127.0.0.1 12000
"""

import sys
import socket
import os.path
import time
import datetime

# Read server IP address and port from command-line arguments
serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
dataLen = 65495

# Create a TCP "welcoming" socket. Notice the use of SOCK_STREAM for TCP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Assign IP address and port number to socket
serverSocket.bind((serverIP, serverPort))

# Listen for incoming connection requests
serverSocket.listen(1)

# loop forever listening for incoming connection requests on "welcoming" socket
while True:
    # Accept incoming connection requests; allocate a new socket for data communication
    connectionSocket, address = serverSocket.accept()

    # Receive and print the client data in bytes from "data" socket
    receivedData = connectionSocket.recv(dataLen).decode()

    try:

        # get the name of the file
        getFileName = receivedData
        splitGetFile = getFileName.splitlines()

        # making a list to save all lines
        fileLine = splitGetFile[0]
        splitFileLine = fileLine.split('/')
        fileName = splitFileLine[1].split(' ')[0]

        # initializing variables
        exists = ''
        currentGMT = ''
        fileTimeGMT = ''
        fileLen = ''
        fileContents = ''

    except IndexError:
        continue

    try:
        # Check if fileName exists
        exists = os.path.isfile(fileName)

        # getting the current time and make it into a string
        nowTime = datetime.datetime.now(datetime.timezone.utc)
        currentGMT = nowTime.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n")

        # getting the time the last time fileName has been modified and make it into GMT
        fileTime = os.path.getmtime(fileName)

        # making the file as a time structure
        fileTimeStruct = time.gmtime(fileTime)

        # convert it as a string
        fileTimeGMT = time.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n", fileTimeStruct)

        # getting len of fileName
        fileLen = os.stat(fileName).st_size

        # save in a string contents of file
        theFile = open(fileName, 'r')
        fileContents = theFile.read()
        theFile.close()

    except FileNotFoundError:
        exits = False

    # variable that will hold the GET Request message
    dataToSend = "HTTP/1.1 "

    # Messages to deliver about the status of filename
    statusOK = '200 OK\r\n'
    statusNoMod = '304 Not Modified\r\n'
    statusNotFound = '404 Not Found\r\n'

    if exists:
        try:
            if not "If-Modified" in receivedData:
                dataToSend += statusOK + \
                              "Date: " + currentGMT + \
                              "Last-Modified: " + fileTimeGMT + \
                              "Content-Length: " + str(fileLen) + "\r\n" + \
                              "Content-Type: text/html; charset=UTF-8\r\n" + \
                              "\r\n" + \
                              fileContents
            else:
                # this block of code is check for 'If-Modified-Since'
                # splitting receivedData in lines
                receivedLines = receivedData.splitlines()

                cacheTimeTuple = ''
                # get the line were it says "If-Modified
                for line in receivedLines:
                     if 'If-Modified' in line:
                        # splitting after the first ': ' since it will have the date/time
                        cacheTime = line.split(": ")
                        # saving the last modification date/time
                        cacheTime = cacheTime[1] + "\r\n"
                        cacheTimeTuple = time.strptime(cacheTime, '%a, %d %b %Y %H:%M:%S %Z\r\n')

                fileTimeGMTTuple = time.strptime(fileTimeGMT, "%a, %d %b %Y %H:%M:%S %Z\r\n")
                cacheSeconds = time.mktime(cacheTimeTuple)
                fileTimeSeconds = time.mktime(fileTimeGMTTuple)

                # this is the case when the file has not been changed
                if cacheSeconds >= fileTimeSeconds:
                    dataToSend += statusNoMod + "Date: " + currentGMT + "\r\n"

                # this is the case when the file changed
                else:
                    dataToSend += statusOK + "Date: " + currentGMT + \
                                  "Last-Modified: " + fileTimeGMT + \
                                  "Content-Length: " + str(fileLen) + "\r\n" + \
                                  "Content-Type: text/html; charset=UTF-8" + "\r\n" + \
                                  "\r\n" + \
                                  fileContents
        except IndexError:
            # this is the case when the file has not been found
            fileLen = 0
            dataToSend += statusNotFound + \
                          "Date: " + currentGMT + \
                          "Content-Length: " + str(fileLen) + "\r\n" + "\r\n"
    else:
        fileLen = 0
        dataToSend += statusNotFound + \
                      "Date: " + currentGMT + \
                      "Content-Length: " + str(fileLen) + "\r\n" + "\r\n"

    print("Data from client: " + receivedData)
    print("Data to be send: ", dataToSend)

    # Echo back to client
    connectionSocket.send(dataToSend.encode())
