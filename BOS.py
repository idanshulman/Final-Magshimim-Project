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

# stats globals
IPS = {}  # all ips collected
COUNTRIES = {}  # all countries  collected
PORTS = {}  # all ports collected
# incoming and outgoing dicts
OUTGOING = {}
INCOMING = {}

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
        print("IP: %s | Country: %s | Direction: %r | Port: %d | Size: %d | Program: %s" % (packet["ip"], packet["country"], packet["direction"], packet["port"], packet["size"], packet["program"]))


def read_setting(settings_file):
    # this function returns a dict of all computers connected and their ip
    users_data = {}  # an empty dict for users
    blacklist_data = {}  # an empty dict for blacklist
    data = settings_file.read()  # read all lines from the file
    users, blacklist = data.split("blacklist:\n")
    blacklist = blacklist.split("\n")  # split the blacklist lines
    users = users.split("\n")  # split the users lines
    # get all users in a dict
    for line in users:
        if line != "":
            address, name = line.split(" : ")  # split data of eac line
            users_data[address] = name  # add data to the dict
    # get all ips in blacklist in a new dict
    for line in blacklist:
        if line != "": # if not an empty line
            ip, site = line.split(" : ")  # split the line into its data
            blacklist_data[ip] = site  # add site data into the dict

    return users_data, blacklist_data  # return value to calling function


def process_data(data, user):
    # this function gets data from a user and adds it to the stats
    for packet in data:  # get all packets from the data collected
        # add ip data
        if packet["ip"] in IPS:
            IPS[packet["ip"]] += packet["size"]   # add one if existing
        else:
            IPS[packet["ip"]] = packet["size"]  # set as one if first appearance

        # add country data
        if packet["country"] in COUNTRIES:
            COUNTRIES[packet["country"]] += packet["size"]  # add one if existing
        else:
            COUNTRIES[packet["country"]] = packet["size"]  # set as one on first appearance

        # todo add program data

        # add ports data
        if packet["port"] in PORTS:
            PORTS[packet["port"]] += packet["size"]
        else:
            PORTS[packet["port"]] = packet["size"]

        # add incoming and outgoing per user
        if not packet["direction"]:  # if incoming (False is incoming therefore not packet["direction"] is used)
            # add incoming data
            if user in INCOMING:
                INCOMING[user] += packet["size"]
            else:
                INCOMING[user] = packet["size"]
        else:
            # add outgoing data
            if user in OUTGOING:
                OUTGOING[user] += packet["size"]
            else:
                OUTGOING[user] = packet["size"]

    return None  # return None - all data saved in globals


def main():
    # this is the main function
    setting_file = open_settings_file()  # now the file is opened and exist
    computers, blacklist_sites = read_setting(setting_file)  # get data from the file
    listening_sock = open_server()  # start listening as a server

    while True:
        # get data and print it
        client_msg, client_addr = listening_sock.recvfrom(DATA_SIZE)  # get data from the
        data = json.loads(client_msg.decode(encoding='UTF-8'))  # translate data using json
        print("\nUser: ", computers[client_addr[0]])  # print the name
        user = computers[client_addr[0]]  # get user name
        process_data(data, user)
        print_packets(data)  # print data


    return None

main()  # call the main function
