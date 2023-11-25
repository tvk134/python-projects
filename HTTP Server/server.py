import socket
import json
import random
import datetime
import hashlib
import sys

def log(message):

    timeStamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    print("SERVER LOG: "+timeStamp+" "+message)

def post(sessions, headers,accFile):
    if 'username' not in headers or 'password' not in headers or not headers['username'] or not headers['password']:
        log("LOGIN FAILED")
        return "HTTP/1.0 501 Not Implemented\r\n\r\n"

    with open(accFile) as json_file:
        data = json.load(json_file)

    username = headers['username']
    password = headers['password']
    
    if username not in data:
        log("LOGIN FAILED: "+username+" : "+password)
        return ("HTTP/1.0 200 OK\r\n\r\nLogin failed!\r\n")

    passTheSalt = data[username]
    hashed = hashlib.sha256()
    hashed.update((password + passTheSalt[1]).encode())
    if(hashed.hexdigest()==passTheSalt[0]):
        cookie = hex(random.randrange(0,(2**64)-1))
        key = "sessionID="+str(cookie)
        sessions[key] = [username,datetime.datetime.now().timestamp()]
        log("LOGIN SUCCESSFUL: "+username+" : "+password)
        #message = 
        #x = "".join([version,message])
        return "HTTP/1.0 200 OK\r\nSet-Cookie: "+key+"\r\n\r\nLogged in!\r\n"
    
    else:
        log("LOGIN FAILED: "+username+" : "+password)
        return ("HTTP/1.0 200 OK\r\n\r\nLogin failed!\r\n")

def get(sessions,headers,version,target,root,timeout):
    key = headers['Cookie'].strip()
    #print(key)
    #print(sessions)
    if not key:
        return "HTTP/1.0 401 Unauthorized\r\n\r\n"
    if not key in sessions:
        log("COOKIE INVALID: "+target)
        return "HTTP/1.0 401 Unauthorized\r\n\r\n"
    sessionInfo = sessions[key]

    currTime = datetime.datetime.now().timestamp()
    if(timeout>=(currTime - sessionInfo[1])):
        sessionInfo[1] = currTime
        filePath = root+sessionInfo[0]+target
        try:
            with open(filePath):
                log("GET SUCCEEDED: "+sessionInfo[0]+" : "+target)
                fileToRead = open(filePath)
                contents = fileToRead.read()
                return "HTTP/1.0 200 OK\r\n\r\n" + contents +"\r\n"
        except FileNotFoundError:
            log("GET FAILED: "+sessionInfo[0]+" : "+target)
            return "HTTP/1.0 404 Not Found\r\n\r\n"
        
    else:
        log("SESSION EXPIRED: "+sessionInfo[0]+" : "+target)
        return "HTTP/1.0 401 Unauthorized\r\n\r\n"



def startServer():
    n = len(sys.argv)
    if n==6:
        IP = sys.argv[1]
        port = sys.argv[2]
        accFile = sys.argv[3]
        timeout = float(sys.argv[4])
        root = sys.argv[5]

        sessions = {}
        HOST,PORT = IP, int(port)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        sock.bind((HOST,PORT))
        
        while True:
            sock.listen(1)
            (conn, address) = sock.accept()
            message = ""
            while True:
                buffer = b''
                while True:
                    content = conn.recv(1)
                    buffer = buffer + content
                    if content == b'\n':
                        break
                #print(buffer)
                if buffer==b"\r\n": break
                message = message + buffer.decode()

            #print(message)
            message = str.replace(message,'\n','\r\n')
            lines = message.split("\r\n")
            startLine = lines[0]
            method,target,version = startLine.split(" ")
            version = version.strip()
            headers = {}
            for header in lines[1:]:
                if header == "": break
                hkey,hval = header.split(": ",1)
                headers[hkey] = hval.strip()
            #print(method,target,version)
            #print(headers)

            if startLine.split(" ")[0]=="POST":
                conn.send(post(sessions,headers,accFile).encode())
                #print(sessions)
            elif startLine.split(" ")[0]=="GET":
                conn.send(get(sessions,headers,accFile,target,root,timeout).encode())
            else: conn.send(("HTTP/1.0 501 Not Implemented\r\n\r\n").encode)

            conn.close()


    else: print("Not enough inputs!")

def main():
    startServer()
          
if __name__ == "__main__":
    main()