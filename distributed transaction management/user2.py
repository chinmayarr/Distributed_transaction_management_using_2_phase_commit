import socket

HOST = 'localhost'
PORT = 10002
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

option=input("Enter the operation:\n1.Balance Enquiry\n2.Withdrawal\n3.Money transfer:");
if(option=="1"):
    data="balance enquiry"
    client_socket.sendall(data.encode())
    received_data = client_socket.recv(1024)
    print("Account balance: Rs ",received_data.decode())

elif(option=="2"): 
    amount=input("Enter the amount you want to withdraw: ")
    data="withdrawal"
    client_socket.sendall(data.encode())
    client_socket.sendall(amount.encode())
    received_data = client_socket.recv(1024)
    print("Withdrawal status:  ",received_data.decode())

elif(option=="3"):
    receiver_ac_no=input("Enter the account number of receiver: ")
    amount=input("Enter the amount you want to transfer: ")
    data="transfer"
    client_socket.sendall(data.encode())
    client_socket.sendall(receiver_ac_no.encode())
    client_socket.sendall(amount.encode())
    received_data = client_socket.recv(1024)
    print("Transaction status: ",received_data.decode())

else:
    print("Invalid entry")

client_socket.close()