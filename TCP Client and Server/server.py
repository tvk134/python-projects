import sys
import hashlib
import socket

def server():
    n = len(sys.argv)
    if(n==3):
        listenPort = sys.argv[1]
        keyFile = sys.argv[2]
        fp = open(keyFile,'r')
        keys = []

        while True:
            content = fp.readline()
            if content == '':
                break
            content = content.strip()
            #print(content)
            keys.append(content)
        
        HOST, PORT = "127.0.0.1", int(listenPort)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        sock.bind((HOST,PORT))
        sock.listen(1)
        (conn, address) = sock.accept()
        data = conn.recv(6)
        incoming = data.decode('ascii')
        if incoming == "HELLO\n":
            print(incoming)
            conn.sendall("260 OK\n".encode('ascii'))
            incoming = conn.recv(5).decode('ascii')
            for x in keys:
                match incoming: 
                    case "QUIT\n":
                        print("QUIT")
                        conn.close()
                        return

                    case "DATA\n":
                        print("DATA")
                        conn.sendall("270 SIG\n".encode("ascii"))
                        hashed = hashlib.sha256()
                        while True:
                            buffer = b''
                            while True:
                                content = conn.recv(1)
                                if content == b'\n':
                                    break
                                buffer = buffer + content
                            buffer = buffer.decode('ascii')
                            if buffer != "":
                                buffer = buffer.replace("\\.",".")
                                if buffer == ".":
                                    break
                                #print(buffer)
                                buffer = buffer + x
                                hashed.update(buffer.encode('ascii'))

                        conn.sendall((hashed.hexdigest()).encode('ascii')+b'\n')
                        incoming = conn.recv(5).decode('ascii')
                        if incoming == "PASS\n" or incoming == "FAIL\n":
                            print(incoming)
                            conn.sendall("260 OK\n".encode('ascii'))
                        else: 
                            print("Communication error!")
                            sock.close()
                            return
                        
                        incoming = conn.recv(5).decode('ascii')
        else:
            print("ERROR! FAILURE TO ESTABLISH CONNECTION")
            sock.close()
            sys.exit()

    else: print("Not enough inputs!")

def main():
    server()
          
if __name__ == "__main__":
    main()