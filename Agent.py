# this is the program for the client in the final project of Maghsimim
from scapy.all import *  # import the scapy lib
import requests  # for http data collection
from scapy.layers.inet import *
import socket
import json
import copy
import netstat_data  # for getting program data
import threading  # for part 3 of the project

# GLOBALS
GEO_IP_ADDR = "http://freegeoip.net"
JSON_ADD = "/json/"
MY_DATA = requests.get(url=str(GEO_IP_ADDR + JSON_ADD)).json()  # getting data from website with no params will be my ip
SERVER_ADDR = '192.168.1.106'
PORT = 42  # the last port

server_addr = (SERVER_ADDR, PORT)  # create a server addr tuple
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a sock object

# get my ip
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # connect socket
s.connect(('8.8.8.8', 1))  # connect to the dns of google
MY_IP = s.getsockname()[0]  # get my ip
s.close()  # close the socket

# directions
INCOMING = False
OUTGOING = True

SNIFF_COUNT = 100

COUNTRIES = {}  # empty dict


class SniffThread(threading.Thread):
    def __init__(self, name_id, num_of_p):
        threading.Thread.__init__(self)
        self.name_id = name_id
        self.packets_number = num_of_p
        self.packets = None
        self.count = 0

    def sniff_packets(self):
        # This is the function that sniffs and process data
        self.packets = sniff(lfilter=packet_filter, count=self.packets_number)  # sniff one packet

    def run(self):
        while True:
            self.sniff_packets()
            th = ProcessThread(self.count, self.packets)
            th.start()
            self.count += 1


class ProcessThread(threading.Thread):
    def __init__(self, name_id, packets):
        threading.Thread.__init__(self)
        self.packets = packets
        self.name_id = name_id
        self.packet_data = {}
        self.packet_list = []

    def process_packets(self, packets):
        netstat_program_data = netstat_data.collect_data()
        for packet in packets:
            self.packet_data["ip"] = get_ip(packet)  # get ip of packet
            self.packet_data["country"] = get_country(packet)  # get country of a packet
            self.packet_data["direction"] = transport_dir(packet)  # get direction of packet false is in, true is out
            self.packet_data["port"] = get_port(packet, self.packet_data["direction"])  # get the port
            self.packet_data["size"] = len(packet)  # get the len of a packet
            try:
                self.packet_data["program"] = netstat_program_data[(self.packet_data["ip"], self.packet_data["port"])]
            except KeyError:
                self.packet_data["program"] = "Unknown"

            self.packet_list.append(copy.copy(self.packet_data))  # add the packet to the list

        return self.packet_list

    def send_message(self, processed_packets):
        send_data = bytes(json.dumps(processed_packets), encoding='UTF-8')
        sock.sendto(send_data, server_addr)  # send data

    def run(self):
        processed_packets = self.process_packets(self.packets)
        self.send_message(processed_packets)


def packet_filter(packet):
    # this is the filter for packets with only ip and tcp or udp
    if IP in packet and (TCP in packet or UDP in packet):
        if packet[IP].src != "104.31.11.172" and packet[IP].src != "104.31.10.172" and packet[IP].dst != "104.31.11.172" and packet[IP].dst != "104.31.10.172":
            return True
        else:
            return False


def get_country(packet):
    # this function get a country of an ip
    county_name = "Unknown"
    if packet[IP].src != MY_IP:  # if the packet is not from this computer
        if packet[IP].src in COUNTRIES:
            county_name = COUNTRIES[packet[IP].src]
        else:
            if not str(packet[IP].src).startswith("192.168") and not str(packet[IP].src).startswith("10.0"):
                url = GEO_IP_ADDR + JSON_ADD + str(packet[IP].src)
                county_name = requests.get(url=url).json()["country_name"]
                COUNTRIES[packet[IP].src] = county_name  # add country to the dict
            elif str(packet[IP].src).startswith("192.168") or str(packet[IP].src).startswith("10.0"):
                county_name = MY_DATA["country_name"]
                COUNTRIES[packet[IP].src] = county_name  # add country to the dict
    else:
        county_name = MY_DATA["country_name"]
    return county_name


def get_ip(packet):
    # this function returns an ip of a packet
    if packet[IP].src != MY_IP:
        ip = packet[IP].src
    elif packet[IP].dst != MY_IP:
        ip = packet[IP].dst
    return ip


def transport_dir(packet):
    # this function finds if a packet is incoming or outgoing
    if str(packet[IP].src) == MY_IP:
        direction = OUTGOING
    else:
        direction = INCOMING
    return direction


def get_port(packet, direction):
    # find the port of a packet not on the client computer
    port = 0
    if direction:  # if out
        if TCP in packet:
            port = packet[TCP].dport
        elif UDP in packet:
            port = packet[UDP].dport
    else:
        if TCP in packet:
            port = packet[TCP].sport
        elif UDP in packet:
            port = packet[UDP].sport

    return port


def main():
    # the main function
    sniff_thread = SniffThread("sniff_thread", SNIFF_COUNT)
    sniff_thread.start()
main()  # call the main function
