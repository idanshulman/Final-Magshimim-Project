import socket
import sys
import json
import time

# GLOBALS
TEMPLATE_PATH = r"C:\Users\magshimim\Documents\Magshimim's Work\Networking\HomeWork\Second Semester\Lesson 12\Project\template\template_edited.html"
OUTPUT_PATH = r"C:\Users\magshimim\Documents\Magshimim's Work\Networking\HomeWork\Second Semester\Lesson 12\Project\HTML Files"
PORT = 42  # the last port
DATA_SIZE = 1024 * 20
SETTINGS_PATH = r"C:/Users/magshimim/Documents/Magshimim's Work/Networking/HomeWork/Second Semester/Lesson 12/Project/PyCharmProj/settings.dat"

# get my ip for server use
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # connect socket
s.connect(('8.8.8.8', 1))  # connect to the dns of google
MY_IP = s.getsockname()[0]  # get my ip
s.close()  # close the socket

# stats globals
IPS = {}  # all ips collected
COUNTRIES = {}  # all countries  collected
PORTS = {}  # all ports collected
PROGRAMS = {}
# incoming and outgoing dicts
OUTGOING = {}
INCOMING = {}
ALERTS = []


def open_server():
    # this function starts listening
    listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a socket object
    server_address = (MY_IP, PORT)
    listening_sock.bind(server_address)
    return listening_sock


def read_setting():
    setting_file = open(SETTINGS_PATH, "r")  # try opening the file
    # this function returns a dict of all computers connected and their ip
    users_data = {}  # an empty dict for users
    blacklist_data = {}  # an empty dict for blacklist
    data = setting_file.read()  # read all lines from the file
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


def process_data(data, user, blacklist_data):
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

        # add program data
        if packet["program"] in PROGRAMS:
            PROGRAMS[packet["program"]] += packet["size"]  # add one if existing
        else:
            PROGRAMS[packet["program"]] = packet["size"]

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

        if packet["ip"] in blacklist_data and (user, packet["ip"]) not in ALERTS:  # if a blacklist site, add to alerts
            ALERTS.append((user, packet["ip"]))  # add packet to alerts

    return None  # return None - all data saved in globals


def write_html():
    # this function writes an html file according the template
    template_file = open(TEMPLATE_PATH, "r")
    template_file_data = template_file.read()  # read all data from the file
    template_file.close()  # close the file
    # Add INCOMING data
    template_file_data = template_file_data.replace("%%incoming_labels%%", str(list(INCOMING.keys())))
    template_file_data = template_file_data.replace("%%incoming_data%%", str(list(INCOMING.values())))
    # Add OUTGOING data
    template_file_data = template_file_data.replace("%%outgoing_labels%%", str(list(OUTGOING.keys())))
    template_file_data = template_file_data.replace("%%outgoing_data%%", str(list(OUTGOING.values())))
    # Add COUNTRIES data
    template_file_data = template_file_data.replace("%%country_labels%%", str(list(COUNTRIES.keys())))
    template_file_data = template_file_data.replace("%%country_data%%", str(list(COUNTRIES.values())))
    # Add IPS data
    template_file_data = template_file_data.replace("%%ip_labels%%", str(list(IPS.keys())))
    template_file_data = template_file_data.replace("%%ip_data%%", str(list(IPS.values())))
    # Add APPS data
    template_file_data = template_file_data.replace("%%app_labels%%", str(list(PROGRAMS.keys())))
    template_file_data = template_file_data.replace("%%app_data%%", str(list(PROGRAMS.values())))
    # Add PORTS data
    template_file_data = template_file_data.replace("%%port_labels%%", str(list(PORTS.keys())))
    template_file_data = template_file_data.replace("%%port_data%%", str(list(PORTS.values())))

    # Add ALERTS data
    template_file_data = template_file_data.replace("%%alerts%%", str(ALERTS))

    # FIND time data
    update_time = time.strftime("%Y-%m-%d | %H:%M:%S")
    template_file_data = template_file_data.replace("%%TIMESTAMP%%", str(update_time))

    # now create a new file
    new_html = open(OUTPUT_PATH + "\\report_file.html", "w")
    new_html.write(template_file_data)
    new_html.close()
    return None


def main():
    # this is the main function
    computers, blacklist_sites = read_setting()  # get data from the file
    listening_sock = open_server()  # start listening as a server

    while True:
        # get data and print it
        client_msg, client_addr = listening_sock.recvfrom(DATA_SIZE)  # get data from the
        data = json.loads(client_msg.decode(encoding='UTF-8'))  # translate data using json
        user = computers[client_addr[0]]  # get user name
        process_data(data, user, blacklist_sites)  # process data
        write_html()  # write data from  globals to file

    return None

main()  # call the main function
