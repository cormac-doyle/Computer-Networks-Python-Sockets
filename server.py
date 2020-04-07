import socket
import select
import sys
import mysql.connector

HEADER_LENGTH = 100

IP = "127.0.0.1"
PORT = 1234

id = 0

# Creates socket
# socket.AF_INET - address family
# socket.SOCK_STREAM - TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# SO_ - socket option
# SOL_ - socket option level
# Sets REUSEADDR (as a socket option) to 1 on socket
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind so server informs operating system that it's going to use given IP and port
# For a server using 0.0.0.0 means to listen on all available interfaces, useful to connect locally to 127.0.0.1 and remotely to LAN interface IP
server_socket.bind((IP, PORT))

# Listen to new connections
server_socket.listen()
# Array of sockets for select.select()
sockets_list = [server_socket]

# List of clients - socket as a key, user header, name as data
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

# Connect to mysql database.
try:
    cnx = mysql.connector.connect(user='root',
                                password='project2',
                               host = '127.0.0.1',
                               database = 'shopstock')
    
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")

cursor = cnx.cursor(buffered = True)

# Handles message receiving
def receive_message(client_socket):
    try:

        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)

        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message

        return False


while True:

    # This is a blocking call, code execution will "wait" here and "get" notified in case any action should be taken
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # Iterate over notified sockets
    for notified_socket in read_sockets:

        # If notified socket is a server socket - new connection, accept it
        if notified_socket == server_socket:

            # Accept new connection
            # That gives us new socket - client socket, connected to this given client only, it's unique for that client
            # The other returned object is ip/port set
            client_socket, client_address = server_socket.accept()

            # Client should send his name right away, receive it
            user = receive_message(client_socket)

            # If False - client disconnected before he sent his name
            if user is False:
                continue

            # Add accepted socket to select.select() list
            sockets_list.append(client_socket)

            # Also save username and username header
            clients[client_socket] = user

            print('New Connection {}:{}, {}'.format(*client_address, user['data'].decode('utf-8')))


        # Else existing socket is sending a message
        else:

            # Receive message
            message = receive_message(notified_socket)

            # If False, client disconnected, cleanup
            if message is False:
                print('Closed Connection: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove from list for socket.socket()
                sockets_list.remove(notified_socket)

                 #Remove from our list of users
                del clients[notified_socket]

                continue

            # Get user by notified socket, so we will know who sent the message
            user = clients[notified_socket]


            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
            print(f'\n{message["data"].decode("utf-8")}\nWAS MESG DATA\n')

            message_decoded = message["data"].decode("utf-8")



            # Iterate over connected clients and broadcast message
            for client_socket in clients:

                # But don't sent it to sender
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    # It's not really necessary to have this, but will handle some socket exceptions just in case
    for notified_socket in exception_sockets:
        # Remove from list for socket.socket()
        sockets_list.remove(notified_socket)

        # Remove from our list of users
        del clients[notified_socket]

def add_shop(cursor, shop_id, name, people):
    id = id + 1
    cmd = "INSERT INTO shop (idshop, shopname, shoppeople) VALUES (\'{}\', \'{}\', \'{}\')".format(id,
                                                                                     name,
                                                                                     people)
    return cursor.execute(cmd)

def get_people_in_shop_name(cursor, shop_name):
    cmd = "SELECT shoppeople FROM shop WHERE shopname = {}".format(str(shop_name))
    cursor.execute(cmd)
    ret = cursor.fetchall()
    if ret:
        return ret[0][0]
    else:
        return False

def shop_exists(cursor, shop_name):
    cmd = "SELECT idshop FROM shop WHERE shopname = \'{}\'".format(str(shop_name))
    cursor.execute(cmd)
    ret = cursor.fetchall()
    if ret:
        return True
    else:
        return False

def update_people(cursor, people, shop_name):
    if shop_exists(cursor, shop_name):
        cmd = "UPDATE shop SET shoppeople = \'{}\' WHERE shopname = \'{}\'".format( str(people), str(shop_name))
        cursor.execute(cmd)
        cnx.commit()
    else:
        id = id+1
        add_shop(cursor, id, shop_name, people)

def get_shop_id(cursor, shop_name):
    cmd = "SELECT idshop FROM shop WHERE shopname = \'{}\'".format(str(shop_name))
    cursor.execute(cmd)
    ret = cursor.fetchall()
    if ret:
        return ret[0][0]
    else:
        return False

def update_stock(cursor, shop_name):
    pass