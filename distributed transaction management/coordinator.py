import socket
import threading
import time
HOST = 'localhost'  
PORT = 1000  
PEERPORT=1002
noofservers=2
noofvotecommits=0
noofcommits=0
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT)) 

server_socket.listen(1)

def handle_connection(client_socket,client_address,id):
    
    global noofvotecommits,noofcommits
    noofcommits=0
    noofvotecommits=0
    time.sleep(waittime)
    if(count<noofservers):
        print("One of the servers is not responding within timeout")
        client_socket.sendall("serverdown".encode())
    else:
        print("\nSending vote_request to server ",id)
        client_socket.sendall("vote_request".encode())
        reply=client_socket.recv(1024).decode()
        print("\nReply from server "+str(id)+"is :"+reply)
        if(reply=="vote_commit"):
            noofvotecommits+=1
        time.sleep(waittime)
        if(noofvotecommits==noofservers):
            print("Sending commit message to server ",id)
            client_socket.sendall("commit".encode())
            if(client_socket.recv(1024).decode()=="success"):
                print("Commit status from server "+str(id)+" is : Success")
                noofcommits+=1
            else:
                print("Commit status from server "+str(id)+"is : failure")
            time.sleep(waittime)
            if(noofcommits==noofservers):
                print("\nSending the transaction success message to server ",id)
                client_socket.sendall("transaction successful".encode())
            else:
                print("\nSending the transaction failure message to server ",id)
                client_socket.sendall("transaction failed".encode())
            
        else:
            print("\nSending abort message to server ",id)
            client_socket.sendall("abort".encode())
    
    client_socket.close()
    
    #check for receiver


    #send data to receiver
count=0
print("Running coordinator......")
waittime=10
id=0
while True :
    client_socket, client_address = server_socket.accept()
    count+=1
    id+=1
    id%=noofservers
    t = threading.Thread(target=handle_connection, args=(client_socket,client_address,id))
    t.start()
server_socket.close()