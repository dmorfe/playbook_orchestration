#!/usr/bin/env python
from pandas.io import excel
from pandas import DataFrame
from netmiko import ConnectHandler
from datetime import datetime
from getpass import getpass
import threading
from threading import Thread
from threading import Lock
from time import time
from queue import Queue
import argparse

TS_LIMIT = 20
QS_LIMIT = 50

default_user = ''
default_pass = ''
default_secret = ''

device_queue = Queue()

# establishes connection to device and returns an object back
def connectToDevice(devcreds):
    ctd = ConnectHandler(**devcreds)
    return(ctd)

# create the header to be saved into log file for every command read from playbook
def get_logheader(commandSent):
    tmp = commandSent + " - " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logHeader = "-" * len(tmp) + "\n" + tmp + "\n" + "-" * len(tmp) + "\n"
    return(logHeader)

# open file to right log
def openlogfile(hostname, ip):
    fileH = open(hostname[:len(hostname)-1] + "-" + str(ip) + ".log",'a')
    return(fileH)

# returns username. function will not exit unless something is entered.
def getusername():
    username = ''
    while username == '':
        username = input('Enter username: ').strip()
    return(username)

# returns username. function will not exit unless something is entered. this function will not allow enty passwords but will allow for passwords with just spaces in it.
def getpassword(usern):
    password = ''
    while password == '':
        password = getpass('Enter ' + usern + ' password: ')
    return(password)

#parse arguments from command line
def getargs():
    parser = argparse.ArgumentParser(description='Playbook Runner by David Morfe')
    parser.add_argument('-i','--inputfile',required=True, help='inputfile name is required.')
    parser.add_argument('-w',required=True,\
     help='specify if configuration should be save into Startup Config.\
     \'Y\' to write config \'N\' to preserve Startup Config. This is a required paramenter.')
    parser.add_argument('-ts',required=True,\
      help='Number of Threads to be created.\nMust be a number from 1 thru 20\nIf a number greater than 20 is entered, the maximum Thread number will be used.')
    parser.add_argument('-qs',required=True,\
      help='Queue size.\nMust be a number from 1 thru 50.\nIf a number greater than 50 is entered, the maximum Queue number will used.')
    parser.add_argument('-o','--outputfile', help='output destination file.')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 6.6')
    args = parser.parse_args()

    if int(args.ts) > TS_LIMIT:
        args.ts = TS_LIMIT

    if int(args.qs) > QS_LIMIT:
        args.qs = QS_LIMIT

    return(args)

# Initializes the threads. Expects an interger as a parameter.
def CreateThreads(n):
    print('Creating ' + n + ' Threads')
    for x in range(int(n)):
        t = Thread(target=ThreadHandler)
        t.daemon = True
        t.start()

def ThreadHandler():
    while True:
        dev_data = device_queue.get()
        MakeChangesAndLog(dev_data)
        device_queue.task_done()
        print(threading.current_thread().name + '-' + dev_data['IP'] + ' Submitted')

def MakeChangesAndLog(rw):
    playbookinfo = {
            'creds' : {
                'device_type' : "",
                'ip' : "",
                'username' : "",
                'password' : "",
                'secret' : "ScHn31d3r" },
            'credsCore' : {
                'device_type' : "",
                'ip' : "",
                'username' : "",
                'password' : "",
                'secret' : "" },
            'listofcommands' : ["show run","show vlan","show int status","show int trunk"]
    }

    playbookinfo['creds']['username'] = default_user
    playbookinfo['creds']['password'] = default_pass
    playbookinfo['credsCore']['username'] = default_user
    playbookinfo['credsCore']['password'] = default_pass
    playbookinfo['creds']['device_type'] = 'cisco_ios'
    playbookinfo['creds']['ip'] = rw.get('IP')
    playbookinfo['credsCore']['ip'] = rw.get('CoreIP')
    playbookinfo['credsCore']['device_type'] = playbookinfo['creds']['device_type']
    portrange = str(rw.get('Metering'))
    vlan = str(rw.get('VLAN'))

    conn = connectToDevice(playbookinfo['creds'])

    resultprompt = conn.find_prompt()
    print('Processing device: ' + playbookinfo['creds']['ip'] + '\n')

    if resultprompt[len(resultprompt)-1] != "#":
        print("Changing from User mode to privilege mode\n" + resultprompt)
        conn.enable()
        resultprompt = conn.find_prompt()
        print(resultprompt)
    else:
        print("Already in privilege mode\n" + resultprompt)
    qalog = openlogfile(resultprompt, playbookinfo['creds']['ip'])
    qalog.write(get_logheader('Port(s) VLAN change - ' + portrange))

    # Log config before changes
    qalog.write('********** BEFORE CHANGES ***********')
    for cmd in playbookinfo['listofcommands']:
        commandresults = conn.send_command(cmd)
        qalog.write(get_logheader(cmd))
        qalog.write(commandresults + '\n\n\n')

    connC = connectToDevice(playbookinfo['credsCore'])
    resultpromptC = connC.find_prompt()

    for cmd in playbookinfo['listofcommands']:
        commandresults = connC.send_command(cmd)
        qalog.write(get_logheader(cmd))
        qalog.write(commandresults + '\n\n\n')

    #resultprompt = conn.config_mode()
    print(resultprompt)

    cmd = ['interface range ' + portrange, 'switchport mode access', 'switchport access vlan ' + vlan, 'description *** python changed ***']
    commandresults = conn.send_config_set(config_commands=cmd)
    qalog.write(commandresults + '\n\n\n')

    cmd = ['interface ' + str(rw.get('IDFTrunk')), 'switchport trunk allowed vlan add ' + vlan]
    cmdC = ['interface ' + str(rw.get('CoreTrunk')), 'switchport trunk allowed vlan add ' + vlan]

    # changing trunk on L2
    commandresults = conn.send_config_set(config_commands=cmd)

    #print ('conf t results back =', commandresults)
    print(resultprompt, '\n', commandresults)

    print('Changing trunk config in Core: ' + playbookinfo['credsCore']['ip'] + '\n')
    commandresultsC = connC.send_config_set(config_commands=cmdC)
    print(connC.find_prompt() + '\n' + commandresultsC + '\n')

    qalog.write(commandresults + '\n\n\n')
    qalog.write(commandresultsC + '\n\n\n')
    commandresults = conn.send_command('wr mem')
    qalog.write(get_logheader('Writing config changes'))
    qalog.write(commandresults + '\n\n\n')

    # Log config after changes
    qalog.write('********** AFTER CHANGES ***********')
    for cmd in playbookinfo['listofcommands']:
        commandresults = conn.send_command(cmd)
        qalog.write(get_logheader(cmd))
        qalog.write(commandresults + '\n\n\n')
    for cmd in playbookinfo['listofcommands']:
        commandresults = connC.send_command(cmd)
        qalog.write(get_logheader(cmd))
        qalog.write(commandresults + '\n\n\n')
    qalog.close()
    conn.disconnect()
    connC.disconnect()

    print('Task Complete For: ' + resultprompt[:len(resultprompt)-1] + '\n\n')

# program entry point
def main():
    global default_user
    global default_pass
    global default_secret

    #read arn parse arguments from command line
    arguments = getargs()

    device_queue.maxsize = int(arguments.qs)

    worksheets = {}

    default_user = getusername()
    default_pass = getpassword(default_user)
    default_secret = getpassword('enable/secret')

    worksheets = {}

    # Initialize threads.
    CreateThreads(arguments.ts)

    with excel.ExcelFile(arguments.inputfile) as wb:
        for sname in wb.sheet_names:
            print("print sheetname: ", sname)
            readsheet = excel.read_excel(wb,sheet_name=sname,converters={'Username':str,'Password':str,'Secret':str,'data_type':str})
            df = DataFrame(data=readsheet, copy=True)
            worksheets[sname] = df.to_dict(orient='records')

            for rw in worksheets[sname]:
                device_queue.put(rw)

    device_queue.join()

    print("All Threads completed successfully!!")

# call main function when program is ran
if __name__ == "__main__":
    main()
