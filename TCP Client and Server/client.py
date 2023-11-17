import sys
import socket

def client():
    n = len(sys.argv)
    if n==5:
        serverName = sys.argv[1]
        port = sys.argv[2]
        messageFileName = sys.argv[3]
        signatureFileName = sys.argv[4]
        fp = open(messageFileName, 'r')
        messages = []
        signatures = []

        while True:
            content = fp.readline()
            if content == '':
                break
            numBytes = int(content)
            content = fp.read(numBytes)
            if content == '':
                break
            content = content + "\n.\n"
            messages.append(content)

        fp = open(signatureFileName,'r')
        while True:
            content = fp.readline()
            if content == '':
                break
            content = content.strip()
            signatures.append(content)
        addr = (serverName,int(port))

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(addr)
        sock.send("HELLO\n".encode("ascii"))
        incoming = sock.recv(7)
        incoming = incoming.decode('ascii')
        print(incoming)
        messageCounter = 0
        for x in messages:
            sock.send("DATA\n".encode('ascii'))
            sock.send(x.encode('ascii'))
            incoming = sock.recv(8).decode('ascii')
            if incoming == "270 SIG\n":
                print(incoming)
                incoming = sock.recv(1024).decode('ascii')
                print(incoming)
                incoming = incoming.strip()
                signatures[messageCounter]
                if(incoming==signatures[messageCounter]):
                    sock.send("PASS\n".encode('ascii'))
                    print ("PASS")
                else: 
                    sock.send("FAIL\n".encode('ascii'))
                    print("FAIL")
                incoming = sock.recv(7).decode('ascii')
                if(incoming != "260 OK\n"):
                    print("Communication error!")
                    sock.close()
                    return
                print(incoming)
            else:
                print("Communication error!")
                sock.close()
                return
            messageCounter = messageCounter + 1

        sock.send(b"QUIT\n")
        print("QUIT")
        sock.close()

    else: print("Not enough inputs!")


def main():
    client()
          
if __name__ == "__main__":
    main()