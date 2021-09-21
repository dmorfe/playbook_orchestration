<a href="https://pypi.org/project/PyPlaybook">
  <img src="https://img.shields.io/pypi/v/pyplaybook.svg" alt="latest release" />
</a>

<a href="https://pepy.tech/project/pyplaybook">
  <img src="https://static.pepy.tech/badge/pyplaybook" alt="downloads" />
</a>

<a href="https://travis-ci.com/github/dmorfe/playbook_orchestration">
  <img src="https://app.travis-ci.com/dmorfe/playbook_orchestration.svg?branch=master&status=passed" />
</a>
# ********* THIS PROGRAM CAN NOW ALSI BE INSTALL AS A Pythom package:
##   - pip install pyplaybook

# Playbook Orchestration tool for Network Engineers.
# SSH or Telnet to supported devices and run commands and save them to a log file. Great for log collection and configration changes in bulk.
# The program can also be used to push configuration changes to supported devices. When pushing configs changes the program will create log with before and after changes.

## PyPlaybook.py:
>> Python tool to automate and orchestrate connecting to network devices and retrieve information and/or make configuration changes.
This tool will allow you to read playbook(s) from an Excel workbook (see Playbook_template.xlsx) and get inquiry and/or config commands and run them against a single or multiple device(s). If the Excel workbook contains multiple tabs/sheets the tool will read all tabs from left to right and execute the statements in the playbook accordingly.(check the excel template for more information on the format and naming convention and sample show and config statements.)

## Port Range VLAN changes.py:
>> This tool will assign/change a port/port range into a vlan on an L2 switch(es) and also add the VLAn to the uplink port on the L2 switch and also add the new VLAN on the distro/core.
The port(s) and VLAN information gets read from an excel workbook (see the Port Range VLAN changes.xlsx template).

>> These programs have been designed to connect to multiple devices at the same time by using Multi Threads which will reduce the amount of time it will take significantly if the tasks are ran as linear process.

## These programs require the following prerequisites Python version and packages:
  ### Dependencies:
    sudo apt update
    sudo apt install software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt install python3.7
    sudo apt install python3-pip
    sudo python3.7 -m pip install --upgrade pip
    sudo ln -s /usr/bin/python3.7 /usr/bin/python

  ### Required Python Version and Libraries:
    - Python 3.x.x or Higher (recommended version 3.7.2)
    - Python packages:
      - netmiko
      - xlrd
      - pandas
      - pandas.io
      - PyYAML

### To install the packages:
      - Linux: sudo pip install xlrd pandas pandas.io netmiko PyYAML
      - Windows(run as administrator): pip install xlrd pandas pandas.io netmiko PyYAML
  
>> - To install the packages for Windows, open a command prompt as an administator and run the same commomand. Make sure you have the lates Python version and PIP has been installed)

>> - Once you have your Python environment setup just drop the Python tools into a folder in the computer you installed Python and give it a go after you finish reading the rest of this Readme file.

>> - The tools need to be run from the CLI and the file containing the playbook (Excel Workbook) needs to be passed as an argument.

>> - To create your playbook(s) you can use the Excel Workbooks provided in the repository. Make sure you don't remove the first row on the first tab of the spreadsheet since all the supported device_type are included on this row and can be selected on the device_type column from the drop down list.

>> - For help on how to run the PyPlaybook.py, run the program without any parameters or with the '-h' flag.<br>
>>    -e.g:<br>
      - python PyPlaybook.py<br>
        usage: PyPlaybook.py [-h] -i INPUTFILE -w W [-v]<br>
      - PyPlaybook.py: error: the following arguments are required: -i/--inputfile, -w<br>
    
  - PyPlaybook.py -h
    - usage: PyPlaybook.py [-h] -i INPUTFILE -w W -ts TS -qs QS [-v]<br>
    - Playbook Runner by David Morfe<br>
    - optional arguments:<br>
    -h, --help            show this help message and exit<br>
    -i INPUTFILE, --inputfile INPUTFILE<br>
                          inputfile name is required.<br>
    -w W                  specify if configuration should be save into Startup<br>
                          Config. 'Y' to write config 'N' to preserve Startup<br>
                          Config. If this flag is not specified or any other<br>
                          value is entered the default will be no to write the<br>
                          config changes. Default: 'N'<br>
    -ts TS                Number of Threads to be created. Must be a number from<br>
                          1 thru 10 If a number greater than 10 is entered, the<br>
                          maximum Thread number will be used. Default: '10'<br>
    -qs QS                Queue size. Must be a number from 1 thru 50. If a<br>
                          number greater than 50 is entered, the maximum Queue<br>
                          number will used. Default: '20'<br>
    -v, --version         show program's version number and exit<br>

These Python programs will create a '.log' file in the current directory from where the programs is run. The name of the .log file is automatically generated based on the device name and the IP address of the device.<br>
<br>
Error handling added to connection object and error loggin added to save error(s) to error.log.<br>
