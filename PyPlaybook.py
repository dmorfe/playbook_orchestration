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

arguments = ''
error_flag = False

TS_LIMIT = 20
QS_LIMIT = 50
TS_DEFAULT = 10
QS_DEFAULT = 20
WRITE_CONFIG_DEFAULT = 'N'

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

# write error to error.log
def write_error_log(devname, errobj):
    msg = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' - Login into: ' + devname + ' failed\n' + \
    '   Error: ' + str(errobj) + '\n'
    print(msg)
    errfh = open('error.log','a')
    errfh.write(msg)
    errfh.close()

# write command header and results to openlogfile
def logshowcommands(qalogH,connH,commands):
    for cmd in commands:
        print(cmd)
        # if cmd is empty skip
        if len(str(cmd).strip()) > 0:
            showresults = connH.send_command(cmd)
            qalogH.write(get_logheader(cmd))
            qalogH.write(showresults + '\n\n')

# returns username. function will not exit unless something is entered.
def getusername():
    username = ''
    while username == '':
        username = input('Enter default username: ').strip()
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
    parser.add_argument('-w', help='specify if configuration should be save into Startup Config.\
     \'Y\' to write config \'N\' to preserve Startup Config. If this flag is not specified or any other \
     value is entered the default will be no to write the config changes.\nDefault: \'N\'')
    parser.add_argument('-ts', help='Number of Threads to be created.\nMust be a number from 1 thru 20\nIf a number \
    greater than 20 is entered, the maximum Thread number will be used.\nDefault: \'10\'')
    parser.add_argument('-qs', help='Queue size.\nMust be a number from 1 thru 50.\nIf a number greater than 50 is \
    entered, the maximum Queue number will used.\nDefault: \'20\'')
    parser.add_argument('-v','--version', action='version', version='%(prog)s 1.8')
    args = parser.parse_args()

    if args.w is None or (args.w.upper() != 'Y' and args.w.upper() != 'N'):
        args.w = WRITE_CONFIG_DEFAULT

    if args.qs is None:
        args.qs = QS_DEFAULT
    elif int(args.qs) > QS_LIMIT:
        args.qs = QS_LIMIT

    if args.ts is None:
        args.ts = TS_DEFAULT
    elif int(args.ts) > TS_LIMIT:
        args.ts = TS_LIMIT

    return(args)

# Initializes the threads. Expects an interger as a parameter.
def CreateThreads(n):
    print('Creating ' + str(n) + ' Threads')
    for x in range(int(n)):
        t = Thread(target=ThreadHandler)
        t.daemon = True
        t.start()

def ThreadHandler():
    while True:
        dev_data = device_queue.get()
        print(threading.current_thread().name + '-' + str(dev_data['IP']).strip() + ' Submitted')
        MakeChangesAndLog(dev_data)
        device_queue.task_done()
        print(threading.current_thread().name + '-' + str(dev_data['IP']).strip() + ' Completed!!')

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

    global arguments
    global error_flag

    playbookinfo['creds']['device_type'] = rw.get('device_type')
    playbookinfo['creds']['ip'] = str(rw.get('IP')).strip()
    # if username field in playbook is blank, interactively enter username
    if rw.get('Username') != rw.get('Username') or rw.get('Username') == '':
        playbookinfo['creds']['username'] = default_user
    else:
        playbookinfo['creds']['username'] = str(rw.get('Username')).strip()
    print('Login into: ' + playbookinfo['creds']['ip'] + ' ...' )
    # if password field in playbook is blank, interactively enter password
    if rw.get('Password') != rw.get('Password') or str(rw.get('Password')).strip() == '':
        playbookinfo['creds']['password'] = default_pass
    else:
        playbookinfo['creds']['password'] = rw.get('Password')
    # if secret field in playbook is blank ask user if it wants to enter one
    if rw.get('Secret') != rw.get('Secret') or rw.get('Secret') == '':
        playbookinfo['creds']['secret'] = default_secret
    else:
        playbookinfo['creds']['secret'] = rw.get('Secret')
    playbookinfo['ShowCommands'] = str(rw.get('Show_Commands')).split('\n')
    playbookinfo['ConfigCommands'] = str(rw.get('Config_Commands')).split('\n')

    # test connection to device. if failed log device info into error.log
    try:
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
                qalog.write(configresults + '\n')
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
        print('close log file and device connection')

    # capture exception error print and log
    except Exception as e:
        error_flag = True
        write_error_log(playbookinfo['creds']['ip'],e)

# program entry point
def main():
    global default_user
    global default_pass
    global default_secret
    global arguments

    #read arn parse arguments from command line
    arguments = getargs()

    # device_queue.maxsize(arguments.qs)
    print('Setting max Queue size to: ', arguments.qs)
    device_queue.maxsize = int(arguments.qs)

    worksheets = {}
    default_user = getusername()
    default_pass = getpassword(default_user)
    default_secret = getpassword('enable/secret')

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

    print(threading.enumerate())
    print('\n')
    if error_flag:
        print('Playbook completed with errors. Check the error.log for device(s) with errors.')
    else:
        print('Playbook completed successfully!!')

# call main function when program is ran
if __name__ == "__main__":
    main()
