import subprocess

# GLOBALS
LOCAL_DATA = 1
FOREIGN_DATA = 2

data = subprocess.getoutput("netstat -nb")
results = []

lines = data.split("\n")

for line in lines:
    line_data = line.split()
    if line_data != []:
        if line_data[0] == "TCP" or line_data[0] == "UDP":
            # a connection indicator line
            local_addr, foreign_addr = line_data[LOCAL_DATA], line_data[FOREIGN_DATA]  # collect data
            local_ip, local_port = local_addr.split(":")  # get local data
            foreign_ip, foreign_port = foreign_addr.split(":")  # get foreign data
            results.append((foreign_ip, foreign_port))
        elif line_data[0].startswith("["):
            # program indicator
            program_data = line_data[0]
            program_name = program_data[program_data.find("[") + 1:program_data.find("]")]
            results.append(program_name)

print(results)

total_data = {}
addresses = []
for item in results:
    if len(item) == 2:
        addresses.append(item)
    else:
        program = item
        total_data[addresses[0]] = program
        addresses = []

print(total_data)
