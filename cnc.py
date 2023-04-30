import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import random
from socket import *
import os
import http.client
import paramiko
import re
import getopt

# Paired with an anonymous VPN/proxy chaining and a VM this would be really secure for pen-testing
# Then again anything with those resources would be decently secure, this would just be more stable as it has multiple servers in one interface so if you lose one it wont be that great of an effect.

# Read servers from servers.txt
servers = open("servers.txt", "r").read().split(',')
#print(str(len(servers)) + " servers read from servers.txt")

clear_cmd = "cls"

if os.name == 'posix':
    clear_cmd = "clear"

# Check internet
try:
    connection = http.client.HTTPSConnection("8.8.8.8", timeout=5)
    connection.request("HEAD", "/")
except:
    exit("No internet connection, please connect to the internet")
finally:
    connection.close()

connected = False

# Ping the servers to dectect the ones that are down
def check_servers(): 

    valid_servers = []
    invalid_servers = open("badservers.txt", "a")

    for server in servers:
        
        # Get hostname of the server we're attempting to ping
        hostname = server.split(":")[0]

        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', hostname]

        # Run the command and check the output
        if subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0:
            # print(hostname + " is up")
            
            # If the server is up, add it to the ret
            valid_servers.append(server)
        else:
            # print(hostname + " is down.")

            invalid_servers.write(hostname + " did not respond\n")

    invalid_servers.close()
    return valid_servers

def exec(server: str, cmd: str):

    try:
        # Get server info in array form [hostname, user, pass]
        info = server.split(":")    
        
        # connect to server throught the SSH protocol.
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(info[0], username=info[1], password=info[2])

        print("connected")

        # Execute the command
        stdin, stdout, stderr = conn.exec_command(cmd)
   
        print(stdout)

        output = stdout.read().decode().strip()
        
        print(output)

        conn.close()
        # Return the output of the command
        return output

    except:
        print("Error connecting to " + info[0])

conn = paramiko.SSHClient()

def ssh_terminal(server: str, shell):
    info = server.split(":")

    global connected

    info = server.split(":")

    if not connected:
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(info[0], username=info[1], password=info[2])
        shell = conn.invoke_shell()
        print(shell.recv(1024).decode())
        connected = True

    command = input(str(info[1]) + "@" + str(info[0]) + " >> ")

    if command.lower() == "exit":
        conn.close()
        shell.close()
        connected = False
        print("bye bye")
        return
    elif command.lower() == "clear":
        os.system(clear_cmd)
    else:
        shell.send((command + '\n').encode())

        print(str(info[1]) + "@" + str(info[0]) + " << " + shell.recv(1024).decode() + "\n", end='')
        
    ssh_terminal(server, shell)

def test_server_logins():
    valid_servers = check_servers()
    invalid_servers = open("badservers.txt", "a")
    to_return = []

    for server in valid_servers:
        # Get server info in array form [hostname, user, pass]
        info = server.split(":")    
        
        try:
            # connect to server throught the SSH protocol.
            conn = paramiko.SSHClient()
            conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            conn.connect(info[0], username=info[1], password=info[2], timeout=1, auth_timeout=1)
            
            ssh_stdin, ssh_stdout, ssh_stderr = conn.exec_command("ls")

            # Sever connection
            conn.close()
        except:
            invalid_servers.write(info[0] + " did not allow for a login via SSH\n")
            continue
        else:
            to_return.append(info[0])

    return to_return

# Get valid servers
valid = check_servers()

def banner(): 
    print("Welcome to the h3 CnC.")
    print(str(len(valid)) + " out of " + str(len(servers)) + " are up.\n")

    print("Input 'help' to see commands")


def handle_args(args: list[str], cmd: str):
    opts, argss = getopt.getopt(args, "hra", ["help=", "rand=", "all="])
    
    for opt, arg in opts:
        if opt == "-h":
            match cmd.lower():
                case 'exec':
                    print("\nDescription: Executes a command on a server via SSH.\n")
                    print("Usage: exec [options] server command")
                    print("OPTIONS := { -h[elp] | -r[and] }\n")
                    return 0
                case 'connect':
                    print("\nDescription: Opens a SSH shell session to a server.\n")
                    print("Usage: connect [options] address:user:pass")
                    print("OPTIONS := { -h[elp] | -r[and] | -a[ll] }\n")
                    return 0
        elif opt == "-a":
            if cmd == 'exec':
                return 2
        elif opt == "-r":
            return 1

def handle_command(command: str):
    
    match command.lower().split():
        case ['exec', *c]: 

            parsed_args = handle_args(c, 'exec')

            if parsed_args == 0:
                return
            
            valid = check_servers()
            cmd = re.findall('"([^"]*)"', command)

            if len(valid) == 0:
                print("No valid servers. ")
                return
            
            if len(cmd) == 0:
                print("No command was stated")
                return

            # Execute on all servers.
            if parsed_args == 2:
                
                for server in valid:
                    print("Executing command on " + server.split(":")[0])

                    # Execute the command
                    ret = exec(server, str(cmd))

                    # Print the command output
                    print("Command output: " + str(ret)) 
            else:
                    
                # Choose a random server index
                server = random.randint(0, len(valid) - 1)

                # Get the selected server information 
                server_info = valid[server]

                print("Executing command on " + server_info.split(":")[0])


                # Execute the command
                ret = exec(server_info, str(cmd))


                # Print the command output
                print("Command output: " + str(ret))

        case ['connect', *params]:

            args = handle_args(params, 'connect')

            if args == 0:
                return

            valid = check_servers()
            server_info = []

            if args == 1 or len(params) == 0: 
                print("Selecting server...")
                
                if len(valid) == 0: 
                    print("No servers are available")
                    return

                # Choose a random server index
                server = random.randint(0, len(valid) - 1)

                # Get the selected server information 
                server_info = valid[server]
            
            else:
                server_info = params[0]


            ssh_terminal(server_info, 0)            

        case ['servers']:
            valid = check_servers()
            print(str(len(valid)) + " out of " + str(len(servers)) + " servers responded to the ping protocol")

            valid_logins = test_server_logins()
            print(str(len(valid_logins)) + " servers allowed for a login on the SSH protocol")

        case ['help']:
            print("\nexec (command) - Execute a command on a random server")
            print("servers - checks which servers are up")
            print("connect (hostname:user:password) - connects via SSH over port 22 to a specified server")
            print("help - prints an index of the commands")
            print("clear - clears the output from previous commands")
            print("reload - reloads the script")
            print("seppuku - deletes the local file and badservers.txt")
            print("exit - exits\n")
    
        case ['exit']:
            os.system(clear_cmd)
            exit()

        case ['reload']:
            exit(os.system("python3 " + __file__))

        case ['clear']:
            os.system(clear_cmd)
            banner()

        case ['seppuku']:
            verify = input("Are you sure you want to delete this file and all traces of it? [Y/N]: ")
            if verify.lower() == "y":
                os.remove("badservers.txt")
                os.remove(__file__)
                exit()

        case _:
            print("Command not recognized. Enter the command 'help' for help")

def main(): 

    command = input("Input >> ")

    handle_command(command)

    main()


if os.name == 'nt':
    os.system("title " + str(len(valid)) + "/" + str(len(servers)) + " servers available")

if __name__ == '__main__':
    os.system(clear_cmd)
    banner()
    main()