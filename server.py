import socket
import select

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

def receive_message(clients_socket):
    try:
        message_header = clients_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False
        
        message_length = int(message_header.decode('utf-8').strip())
        return {'header': message_header, 'data': clients_socket.recv(message_length)}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            clients_socket, client_address = server_socket.accept()

            user = receive_message(clients_socket)
            if user is False:
                continue
            sockets_list.append(clients_socket)
            clients[clients_socket] = user
            print(f"accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")
        else:
            message = receive_message(notified_socket)

            if message is False:
                print(f"closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f"received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for clients_socket in clients:
                if clients_socket != notified_socket:
                    clients_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
                
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]