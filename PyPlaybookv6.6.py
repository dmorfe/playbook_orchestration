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

# default show commands
SHOWCOMMANDS = ['show run','show interface status','show vlan']
TS_LIMIT = 20
QS_LIMIT = 50
common_user = ''
common_pass = ''
common_secret = ''

device_queue = Queue(50)

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

# write command header and results to openlogfile
def logshowcommands(qalogH,connH,commands):
    for cmd in commands:
        print(cmd)
        showresults = connH.send_command(cmd)
        qalogH.write(get_logheader(cmd))
        qalogH.write(showresults + '\n\n')

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
     \'Y\' to write config \'N.\ to preserve Startup Config. This is a required paramenter.')
    parser.add_argument('-ts',required=True,\
      help='Number of Threads to be created.\nMust be a number from 1 thru 20\NIf a number greater than 20 is entered, the maximum Thread number will be used.')
    parser.add_argument('-qs',required=True,\
      help='Queue size.\nMust be a number from 1 thru 50.\nIf a number greater than 50 is entered, the maximum Queue number will used.')
    parser.add_argument('-o','--outputfile', help='output destination file.')
    args = parser.parse_args()

    if args.ts > TS_LIMIT:
        args.ts = TS_LIMIT

    if args.qs > QS_LIMIT:
        args.qs = QS_LIMIT

    return(args)

def CreateThreads(n):
    print('Creating ' + n + ' Threads')
    for x in range(n):
        t = Thread(target=ThreadHandler)
        t.deamon = True
        t.start()

def ThreadHandler()
    while True:
        dev_data = device_queue.get()
        MakeChangesAndLog(dev_data)
        dev_data.task_done()
        print(threading.current_thread().name + '-' + dev_data['ip'] + 'Submitted')

# Connects to device runs commands and creates and log file
def MakeChangesAndLog(rw):
    playbookinfo = {
            'creds' : {
                'device_type' : "",
                'ip' : "",
                'username' : "",
                'password' : "",
                'secret' : "" },
            'ShowCommands' : [],
            'ConfigCommands' : []
    }

    playbookinfo['creds']['device_type'] = rw.get('device_type')
    playbookinfo['creds']['ip'] = rw.get('IP')
    # if username field in playbook is blank, interactively enter username
    if rw.get('Username') != rw.get('Username') or rw.get('Username').strip() == '':
        playbookinfo['creds']['username'] = common_user()
    else:
        playbookinfo['creds']['username'] = rw.get('Username')
    print('Login into: ' + playbookinfo['creds']['ip'] + ' ...' )
    # if password field in playbook is blank, interactively enter password
    if rw.get('Password') != rw.get('Password') or rw.get('Password').strip() == '':
        playbookinfo['creds']['password'] = common_pass
    else:
        playbookinfo['creds']['password'] = rw.get('Password')
    # if secret field in playbook is blank ask user if it wants to enter one
    if rw.get('Secret') != rw.get('Secret') or rw.get('Secret') == '':
        playbookinfo['creds']['secret'] = common_secret
    else:
        playbookinfo['creds']['secret'] = rw.get('Secret')
    playbookinfo['ShowCommands'] = str(rw.get('Show_Commands')).split('\n')
    playbookinfo['ConfigCommands'] = str(rw.get('Config_Commands')).split('\n')

    conn = connectToDevice(playbookinfo['creds'])
    resultprompt = conn.find_prompt()

    if resultprompt[len(resultprompt)-1] != "#":
        print("----> Changing from User mode to privilege mode <----\n" + resultprompt)
        conn.enable()
        resultprompt = conn.find_prompt()
        print(resultprompt)
    else:
        print("----> Already in privilege mode <----\n" + resultprompt)
    qalog = openlogfile(resultprompt, playbookinfo['creds']['ip'])
    if (rw.get('Show_Commands') == rw.get('Show_Commands')) and \
    len(str(rw.get('Show_Commands')).strip()) > 0 and rw.get('Config_Commands') != rw.get('Config_Commands'):
        print(\
              '*****************************************************\n' + \
              '***               Running show commands           ***\n' + \
              '*****************************************************\n')
        logshowcommands(qalog,conn,playbookinfo['ShowCommands'])
    if (rw.get('Config_Commands') == rw.get('Config_Commands')) and \
    len(str(rw.get('Config_Commands')).strip()) > 0:
        print(\
              '*****************************************************\n' + \
              '***                Entering config mode           ***\n' + \
              '*****************************************************\n')
        print(\
              '*****************************************************\n' + \
              '***    Running show commands - before changes     ***\n' + \
              '*****************************************************\n')
        qalog.write(\
              '*****************************************************\n' + \
              '***    Running show commands - before changes     ***\n' + \
              '*****************************************************\n')
        if rw.get('Show_Commands') == rw.get('Show_Commands'):
            logshowcommands(qalog,conn,playbookinfo['ShowCommands'])
        else:
            logshowcommands(qalog,conn,SHOWCOMMANDS)
        configresults = conn.send_config_set(config_commands=playbookinfo['ConfigCommands'])
        print(\
              '*****************************************************\n' + \
              '***              Configurations Changes           ***\n' + \
              '*****************************************************\n')
        print( configresults)
        qalog.write(get_logheader('Configuration changes'))
        qalog.write(configresults + '\n')
        if arguments.w.upper() == 'Y':
            print(\
                  '*****************************************************\n' + \
                  '***   Writing Running Config to Startup Config    ***\n' + \
                  '*****************************************************\n')
            qalog.write(\
                  '*****************************************************\n' + \
                  '***   Writing Running Config to Startup Config    ***\n' + \
                  '*****************************************************\n')
            configresults = conn.send_command('write mem')
            print(configresults)
            qalog.write(configresults)
        print(\
              '*****************************************************\n' + \
              '*** Running show commands - after configurations  ***\n' + \
              '*****************************************************\n')
        qalog.write(\
          '*****************************************************\n' + \
          '*** Running show commands - after configurations  ***\n' + \
          '*****************************************************\n')
        if rw.get('Show_Commands') == rw.get('Show_Commands'):
            logshowcommands(qalog,conn,playbookinfo['ShowCommands'])
        else:
            logshowcommands(qalog,conn,SHOWCOMMANDS)

    qalog.close()
    conn.disconnect()

# program entry point
def main():
    #read arn parse arguments from command line
    arguments = getargs()

    worksheets = {}
    common_user = getusername()
    common_pass = getpassword(common_user)
    common_secret = getpassword('enable/secret')

    # Initializes the threads.
    CreateThreads(arguments.ts)

    with excel.ExcelFile(arguments.inputfile) as wb:
        for sname in wb.sheet_names:
            print('**** Sheet Name: '+ str(sname))
            readsheet = excel.read_excel(wb,sheet_name=sname,converters={'Username':str,'Password':str,'Secret':str,'data_type':str,'Show_Commands':str,'Config_Commands':str})
            df = DataFrame(data=readsheet, copy=True)
            worksheets[sname] = df.to_dict(orient='records')

            for rw in worksheets[sname]:
                device_queue.put(rw)

    device_queue.join()

    print('Playbook completed successfully!!')

# call main function when program is ran
if __name__ == "__main__":
    main()
