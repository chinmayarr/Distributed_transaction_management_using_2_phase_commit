import socket
import threading
import time
HOST = 'localhost'
PORT = 10001
CPORT=1000
PEERPORT1=1001
PEERPORT2=1002
lock = threading.Lock()
receiver_ac_no="" 
transamount=""
class Account:
    def __init__(self, account_number, balance):
        self.account_number = account_number
        self.balance = balance
    
    def deposit(self, amount):
        self.balance += amount
    
    def withdraw(self, amount):
        self.balance -= amount
    
    def get_balance(self):
        return self.balance
    
    def __str__(self):
        return f"Account number: {self.account_number}, Balance: {self.balance}"

#create account of user1
user1=Account(1111,50000)

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
peerserversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to a specific address and port
server_socket.bind((HOST, PORT))
peerserversocket.bind((HOST, PEERPORT1))

# Set the maximum number of queued connections
server_socket.listen(1)
peerserversocket.listen(1)

def peerserver():
    while True:
        socket1,addr=peerserversocket.accept()
        global receiver_ac_no,transamount
        # receiver_ac_no=socket.recv(1024)
        transamount=socket1.recv(1024)
        cordsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cordsocket.connect((HOST,CPORT))
        reply=cordsocket.recv(1024).decode()
        if(reply=="vote_request"):
            print("Got vote_request from coordinator")
            choice=input("\nEnter your choice\n1.vote_commit\n2.vote_abort\n")
            if(choice=="1"):
                cordsocket.send("vote_commit".encode())
            elif(choice=="2"):
                cordsocket.send("vote_abort".encode())
            reply=cordsocket.recv(1024).decode()
            if(reply=="commit"):
                print("Got commit message from coordinator")
                with lock:
                    user1.deposit(int(transamount.decode()))
                    choice=input("\nEnter your choice\n1.success\n2.failure\n")
                    if(choice=="1"):
                        cordsocket.send("success".encode())
                    elif(choice=="2"):
                        cordsocket.send("failure".encode())
                if(cordsocket.recv(1024).decode()=="transaction failed"):
                    print("Got transaction failure message from coordinator.Rolling back the transaction..")
                    with lock:
                        user1.withdraw(int(transamount.decode()))
                else:
                    print("Got transaction success message from coordinator")
            elif(reply=="abort"):
                print("Got abort message from coordinator")

        cordsocket.close()
        socket1.close()


def handle_connection(client_socket,addr):
    data=client_socket.recv(1024).decode()
    if(data=="balance enquiry"):
        balance=user1.get_balance()
        client_socket.sendall(str(balance).encode())
        return
    
    elif(data=="withdrawal"):
        status="Success"
        amount=client_socket.recv(1024)
        if int(amount.decode()) > user1.get_balance():
            status="Insufficient balance"
        else:
            with lock:
                user1.withdraw(int(amount.decode()))
        client_socket.sendall(status.encode())

    elif(data=="transfer"):
        receiver_ac_no=client_socket.recv(1024)
        amount=client_socket.recv(1024)
        if int(amount.decode()) > user1.get_balance():
            status="Money transfer failed:Insufficient balance"
            client_socket.send(status.encode())
        else:
            peerclientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerclientsocket.connect((HOST,PEERPORT2))
            # peerclientsocket.send(receiver_ac_no)
            peerclientsocket.send(amount)
            peerclientsocket.close()
            cordsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cordsocket.connect((HOST,CPORT))
            reply=cordsocket.recv(1024).decode()
            if(reply=="vote_request"):
                print("got vote_request from coordinator")
                cordsocket.send("vote_commit".encode())
                reply=cordsocket.recv(1024).decode()
                if(reply=="commit"):
                    print("Got commit message from coordinator")
                    with lock:
                        user1.withdraw(int(amount.decode()))
                        cordsocket.send("success".encode())
                    if(cordsocket.recv(1024).decode()=="transaction failed"):
                        print("Got transaction failure message from coordinator.Rolling back the transaction..")
                        with lock:
                            user1.deposit(int(amount.decode()))
                            client_socket.sendall("Money transfer failed".encode())
                    else:
                        print("Got transaction success message from coordinator")
                        client_socket.sendall("Money transfer successful".encode())
                
                elif(reply=="abort"):
                    print("Got abort message from coordinator")
                    client_socket.sendall("Money transfer failed".encode())
            elif (reply=="serverdown"):
                print("Transaction failed due to server issues")
                client_socket.sendall("Money transfer failed".encode())
            cordsocket.close()
 
t1=threading.Thread(target=peerserver, args=())
t1.start()

while True:
    client_socket, client_address = server_socket.accept()
    t2 = threading.Thread(target=handle_connection, args=(client_socket,client_address))
    t2.start()

# Close the server socket
server_socket.close()