
# Playbook Orchestration tool for Network Engineers. Orchestration Tool for Network Engineers.
Python tool to automate and orchestrate connecting to network devices and retrieve information and/or make configuration changes.
This tool will allow you to read playbook(s) from an Excel workbook and get inquiry and/or config commands and run them against a sigle or multiple device(s). If the Excel workbook contains multiple tabs/sheets the tool will read all tabs from left to right and execute the statements in the playbook accordingly.(check the excel template for more information on the format and naming convention and sample show and config statements.)

This program has been designed to connect to multiple devices at the same time by using Multi Threads which will reduced significantly the amount of time it will take if the tasks are ran as a linear process.

# This program requires the following Python version and packages:
  - Python 3.x.x or Higher (recommended version 3.7.2)
  - Python packages:
    - netmiko
    - xlrd
    - pandas

# To install the packages:
    - Linux: sudo pip install xlrd pandas netmiko
  
To install the packages for Windows, open a command prompt as an administator and run the same commomand. Make sure you have the lates Python version and PIP has been installed)

Once you have your Python environment setup just drop the PyPlaybook.py into a folder in computer you installed Python and give it a go after you finish reading the rest of this Readme file.

The tool needs to be run from the CLI and the file containing the playbook (Excel Workbook) needs to be pass arguments.

To create your playbook(s) you can use the Excel Workbook provided in the repository. Make sure you don't remove the first row on the first tab of the spreadsheet since all the supported device_type are include on this raw and can be selected on the device_type column from the drop down list.

For help on how to run the PyPlaybook.py, run the program without any parameters or with the '-h' flag.
e.g:
  - python PyPlaybook.py
    usage: PyPlaybookv6.6.py [-h] -i INPUTFILE -w W -ts TS -qs QS [-o OUTPUTFILE]
                             [-v]
    PyPlaybookv6.6.py: error: the following arguments are required: -i/--inputfile, -w, -ts, -qs
    
  - PyPlaybook.py -h
  
    usage: PyPlaybookv6.6.py [-h] -i INPUTFILE -w W -ts TS -qs QS [-o OUTPUTFILE]
                [-v]
    
    Playbook Runner by David Morfe
    
    optional arguments:
    -h, --help            show this help message and exit
    -i INPUTFILE, --inputfile INPUTFILE
                inputfile name is required.
    -w W                  specify if configuration should be save into Startup
                Config. 'Y' to write config 'N' to preserve Startup
                Config. This is a required paramenter.
    -ts TS                Number of Threads to be created. Must be a number from
                1 thru 20 If a number greater than 20 is entered, the
                maximum Thread number will be used.
    -qs QS                Queue size. Must be a number from 1 thru 50. If a
                number greater than 50 is entered, the maximum Queue
                number will used.
    -o OUTPUTFILE, --outputfile OUTPUTFILE
                output destination file.
    -v, --version         show program's version number and exit

This playbook will create a '.log' file in the current directory from where the PyPlaybook is ran. The name of the .log file is automatically generated based on the device name and the IP address of the device.
