#!/usr/bin/env python
# Version 6.5 as of 2/26/2019
from pandas.io import excel
from pandas import DataFrame
from netmiko import ConnectHandler
from datetime import datetime
from getpass import getpass
import argparse

# default show commands
SHOWCOMMANDS = ['show run','show interface status','show vlan']

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
    parser = argparse.ArgumentParser(description='Playbook Orchestration by David Morfe - February 2019')
    parser.add_argument('-i','--inputfile',required=True, help='inputfile name is required.' )
    parser.add_argument('-w',required=True,\
     help='specify if configuration should be save into Startup Config.\
     \'Y\' to write config \'N.\ to preserve Startup Config. This is a required paramenter.' )
    parser.add_argument('-v','--version', action='version', version='%(prog)s 1.5')
    args = parser.parse_args()
    return(args)

# program entry point
def main():
    #read arn parse arguments from command line
    arguments = getargs()

    worksheets = {}

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

    with excel.ExcelFile(arguments.inputfile) as wb:
        playbookinfo['ShowCommands'] = ''
        playbookinfo['ConfigCommands'] = ''
        for sname in wb.sheet_names:
            print('**** Sheet Name: ' + str(sname))
            readsheet = excel.read_excel(wb,sheet_name=sname,converters={'Username':str,'Password':str,'Secret':str,\
            'data_type':str,'Show_Commands':str,'Config_Commands':str})
            df = DataFrame(data=readsheet, copy=True)
            worksheets[sname] = df.to_dict(orient='records')

            for rw in worksheets[sname]:
                playbookinfo['creds']['device_type'] = rw.get('device_type')
                playbookinfo['creds']['ip'] = rw.get('IP')

                # if username field in playbook is blank, interactively enter username
                if rw.get('Username') != rw.get('Username') or rw.get('Username').strip() == '':
                    playbookinfo['creds']['username'] = getusername()
                else:
                    playbookinfo['creds']['username'] = rw.get('Username')

                print('\nLogin into: ' + playbookinfo['creds']['ip'] + ' ...' )
                # if password field in playbook is blank, interactively enter password
                if rw.get('Password') != rw.get('Password') or rw.get('Password').strip() == '':
                    playbookinfo['creds']['password'] = getpassword(playbookinfo['creds']['username'])
                else:
                    playbookinfo['creds']['password'] = rw.get('Password')

                # if secret field in playbook is blank ask user if it wants to enter one
                if rw.get('Secret') != rw.get('Secret') or rw.get('Secret') == '':
                    if input('do you want to enter enabled/secret password(Y/N): ').upper() == 'Y':
                        playbookinfo['creds']['secret'] = getpassword('secret/enabled')
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
                    print(configresults)
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
            print('\n**** Task(s) Completed with no errors ****')

# call main function when program is ran
if __name__ == "__main__":
    main()
