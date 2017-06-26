# this is the program for the client in the final project of Maghsimim
from scapy.all import *  # import the scapy lib
import requests  # for http data collection
from scapy.layers.inet import *
import socket
import json
import copy

# GLOBALS
GEO_IP_ADDR = "http://freegeoip.net"
JSON_ADD = "/json/"
MY_DATA = requests.get(url=str(GEO_IP_ADDR + JSON_ADD)).json()  # getting data from website with no params will be my ip
SERVER_ADDR = 'localhost'
PORT = 42  # the last port

# get my ip
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # connect socket
s.connect(('8.8.8.8', 1))  # connect to the dns of google
MY_IP = s.getsockname()[0]  # get my ip
s.close()  # close the socket

# directions
INCOMING = False
OUTGOING = True

SNIFF_COUNT = 20

COUNTRIES = {}  # empty dict


def contain_tcp_udp_ip(packet):
    # this is the filter for packets with only ip and tcp or udp
    return IP in packet and (TCP in packet or UDP in packet)


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


def sniff_packets(num_of_packets):
    # This is the function that sniffs and process data
    packet_data = {}
    packet_list = []
    packets = sniff(lfilter=contain_tcp_udp_ip, count=num_of_packets)  # sniff one packet
    for packet in packets:
        packet_data["ip"] = get_ip(packet)  # get ip of packet
        packet_data["country"] = get_country(packet)  # get country of a packet
        packet_data["direction"] = transport_dir(packet)  # get direction of packet false is in, true is out
        packet_data["port"] = get_port(packet, packet_data["direction"])  # get the port
        packet_data["size"] = len(packet)  # get the len of a packet
        packet_list.append(copy.copy(packet_data))  # add the packet to the list

    return packet_list


def main():
    # the main function
    server_addr = (SERVER_ADDR, PORT)  # create a server addr tuple
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a sock object
    while True:
        packets = sniff_packets(SNIFF_COUNT)  # get packets and add them to the PACKET_LIST global
        send_data = bytes(json.dumps(packets), encoding='UTF-8')
        sock.sendto(send_data, server_addr)  # send data

main()  # call the main function
