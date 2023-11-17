#!/usr/bin/env python

'''
CS352 Assignment 1: Network Time Protocol
You can work with 1 other CS352 student

DO NOT CHANGE ANY OF THE FUNCTION SIGNATURES BELOW
'''

from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime
import socket

def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float, float):
    # add your code here 
    addr = (server,port)
    send = '\x1b' + 47 * '\0'

    sock = socket.socket(AF_INET,SOCK_DGRAM)
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    T1 = secs + float(time_difference.microseconds / 1000000.0)
    sock.sendto(send.encode('utf-8'),addr)
    pkt,addr = sock.recvfrom(1024)
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    T4 = secs + float(time_difference.microseconds / 1000000.0)
    return (pkt, T1, T4)


def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    
    T2 = float (struct.unpack( "!12I", pkt )[8] + ((struct.unpack( "!12I", pkt )[9] /pow(2,32))))
    T2-=2208988800

    T3 = float (struct.unpack( "!12I", pkt )[10] + ((struct.unpack( "!12I", pkt )[11]/pow(2,32))))
    T3-=2208988800

    rtt = (T4-T1) - (T3-T2)
    offset = ((T2-T1)+(T3-T4))/2
    return (rtt, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20) -> float:
    offsets = []
    for x in range(0,iters):
        (pkt,T1,T4) = getNTPTimeValue()
        (rtt,offset) = ntpPktToRTTandOffset(pkt,T1,T4)    
        offsets.append(offset)
    avg = 0
    for y in(offsets):
        avg+=y
    avg/=20
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    timestamp_float = secs + float(time_difference.microseconds / 1000000.0)
    currentTime = timestamp_float+avg
    return currentTime


if __name__ == "__main__":

    print(getCurrentTime())
