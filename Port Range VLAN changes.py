#!/usr/bin/env python
from pandas.io import excel
from pandas import DataFrame
from netmiko import ConnectHandler
from datetime import datetime
from getpass import getpass

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

# program entry point
def main():
    #creds = get_devinfo()

    worksheets = {}

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

    with excel.ExcelFile("Cellar metering ports.xlsx") as wb:
        for sname in wb.sheet_names:
            print("print sheetname: ", sname)
            readsheet = excel.read_excel(wb,sheet_name=sname,converters={'Username':str,'Password':str,'Secret':str,'data_type':str})
            df = DataFrame(data=readsheet, copy=True)
            worksheets[sname] = df.to_dict(orient='records')
            playbookinfo['creds']['username'] = getusername()
            playbookinfo['creds']['password'] = getpassword(playbookinfo['creds']['username'])
            playbookinfo['credsCore']['username'] = playbookinfo['creds']['username']
            playbookinfo['credsCore']['password'] = playbookinfo['creds']['password']

            for rw in worksheets[sname]:
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
                cmd = 'vlan ' + vlan + '\nname Metering-VLAN\n' + 'interface range ' + portrange + '\n' + 'switchport mode access\nswitchport access vlan ' \
                + vlan + '\ndescription *** Metering Port ***\nend\n'
#                cmd = ['interface range ' + portrange, 'switchport mode access', 'switchport access vlan ' + vlan, 'description *** python changed ***']

                commandresults = conn.send_config_set(config_commands=cmd)
                qalog.write(commandresults + '\n\n\n')

                cmd = 'interface ' + rw.get('IDFTrunk') + '\n' + 'switchport trunk allowed vlan add ' + vlan + '\n'
                cmdC = 'interface ' + rw.get('CoreTrunk') + '\n' + 'switchport trunk allowed vlan add ' + vlan + '\n'

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
# call main function when program is ran
if __name__ == "__main__":
    main()
