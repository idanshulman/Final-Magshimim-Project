import socket
import sys
import json
import threading

# GLOBALS
PORT = 42  # the last port
SETTINGS_FILE_NAME = "settings.dat"
DATA_SIZE = 1024 * 20
PATH = sys.argv[0]

# get my ip for server use
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # connect socket
s.connect(('8.8.8.8', 1))  # connect to the dns of google
MY_IP = s.getsockname()[0]  # get my ip
s.close()  # close the socket

counter = len(PATH) - 1

# find the
while counter > 1:
    if PATH[counter] == '\\' or PATH[counter] == '/':
        counter += 1
        break
    else:
        counter -= 1

PATH = PATH[0:counter]


def open_settings_file():
    try:
        setting_file = open(PATH + SETTINGS_FILE_NAME, "r")  # try opening the file
    except FileNotFoundError:
        setting_file = open(PATH + SETTINGS_FILE_NAME, "a")  # create the file if not exist
    return setting_file


def open_server():
    # this function starts listening
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a socket object
    server_address = (MY_IP, PORT)
    listening_sock.bind(server_address)
    return listening_sock


def print_packets(packets):
    # this function prints packet list to the boss
    for packet in packets:
        print("IP: %s | Country: %s | Direction: %r | Port: %d | Size: %d" % (packet["ip"], packet["country"], packet["direction"], packet["port"], packet["size"]))


def read_setting(settings_file):
    # this function returns a dict of all computers connected and their ip
    new_dict = {}  # an empty dict
    data = settings_file.read()  # read all lines from the file
    data = data.split("\n")
    for line in data:
        if line != "":
            address, name = line.split(" : ")  # split data of eac line
            new_dict[address] = name  # add data to the dict

    return new_dict  # return value to calling function


def main():
    # this is the main function
    setting_file = open_settings_file()  # now the file is opened and exist
    computers = read_setting(setting_file)
    listening_sock = open_server()  # start listening as a server

    while True:
        # get data and print it
        client_msg, client_addr = listening_sock.recvfrom(DATA_SIZE)  # get data from the
        data = json.loads(client_msg.decode(encoding='UTF-8'))  # translate data using json
        print("\nUser: ", computers[client_addr[0]])  # print the name
        print_packets(data)  # print data

    return None

main()  # call the main function
