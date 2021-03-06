import subprocess

# GLOBALS
LOCAL_DATA = 1
FOREIGN_DATA = 2


def collect_data():
    # this function collects data from the function netstat -nb for program data
    data = subprocess.getoutput("netstat -nb")  # get output of the program
    split_data = []  # results

    lines = data.split("\n")  # split data

    for line in lines:  # get a list of one tuple and than a string of a program
        line_data = line.split()
        if line_data != []:
            if (line_data[0] == "TCP" or line_data[0] == "UDP") and not line_data[LOCAL_DATA].startswith("["):
                # a connection indicator line
                local_addr, foreign_addr = line_data[LOCAL_DATA], line_data[FOREIGN_DATA]  # collect data
                local_ip, local_port = local_addr.split(":")  # get local data
                foreign_ip, foreign_port = foreign_addr.split(":")  # get foreign data
                split_data.append((foreign_ip, int(foreign_port)))
            elif line_data[0].startswith("["):
                # program indicator
                program_data = line_data[0]  # find program name
                program_name = program_data[program_data.find("[") + 1:program_data.find("]")]  # remove additional []
                split_data.append(program_name)  # add it to the main list

    data_dict = {}
    addresses = []
    for item in split_data:  # convert the list into a dict
        if len(item) == 2 and type(item) is tuple:
            addresses.append(item)
        elif type(item) is str:
            program = item
            for address in addresses:
                data_dict[address] = program
            addresses = []
    # in total data - the key is tuple - (ip, port) and the value is the program used by this ip and port
    # the packet with the save ip and port will be the one which uses the program

    del split_data  # we do not need results any more

    return data_dict  # return the dict to the calling function
