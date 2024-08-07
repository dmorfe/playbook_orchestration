<a href="https://pypi.org/project/PyPlaybook"> <img src="https://img.shields.io/pypi/v/pyplaybook.svg" alt="latest release" /> </a>
<a href="https://pepy.tech/project/pyplaybook"> <img src="https://static.pepy.tech/badge/pyplaybook" alt="downloads" /> </a>


# Playbook Orchestration tool for Network Engineers. Orchestration Tool for Network Engineers.

## PyPlaybook:

Python tool to automate and orchestrate connecting to network devices and retrieve information and/or make configuration changes. This tool will allow you to read playbook(s) from an Excel workbook (see Playbook_template.xlsx) and get inquiry and/or config commands and run them against a single or multiple device(s). If the Excel workbook contains multiple tabs/sheets the tool will read all tabs from left to right and execute the statements in the playbook accordingly.(check the excel template for more information on the format and naming convention and sample show and config statements.)

**** This tool can also be used as an imported library from PyPi:
- `pip install PyPlaybook`
- ```py
  import PyPlaybook
  config = PyPlaybook.Orchestration(input_file, w=None, ts=None, qs=None, delay=None, username=None, password=None, secret=None)
  config.run()```

## Port Range VLAN changes:

- This tool will assign/change a port/port range into a vlan on an L2 switch(es) and also add the VLAn to the uplink port on the L2 switch and also add the new VLAN on the distro/core. The port(s) and VLAN information gets read from an excel workbook (see the Port Range VLAN changes.xlsx template).

- These programs have been designed to connect to multiple devices at the same time by using Multi Threads which will reduce the amount of time it will take significantly if the tasks are ran as linear process.

## This tool requires the following prerequisite packages:

### Dependencies:

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt install python3-pip
sudo python3.7 -m pip install --upgrade pip
sudo ln -s /usr/bin/python3.7 /usr/bin/python
```

### Required Python Version and Libraries:

```
- Python 3.x.x or Higher (recommended version 3.7.2)
- Python packages:
  - netmiko
  - xlrd
  - pandas
  - PyYAML
```

### To install the packages:

```
  - Linux: sudo pip install xlrd pandas netmiko PyYAML
  - Windows(run as administrator): pip install xlrd pandas netmiko PyYAML
```

* To install the packages for Windows, open a command prompt as an administator and run the same commomand. Make sure you have the latest Python version and PIP has been installed)

* Once you have your Python environment setup just drop the Python tools into a folder in the computer you installed Python and give it a go after you finish reading the rest of this Readme file.

* The tools need to be run from the CLI and the file containing the playbook (Excel Workbook) needs to be passed as an argument.

* To create your playbook(s) you can use the Excel Workbooks provided in the repository. Make sure you don't remove the first row on the first tab of the spreadsheet since all the supported device_type are included on this row and can be selected on the device_type column from the drop down list.

* For help on how to run the PyPlaybook.py, run the program without any parameters or with the '-h' flag.<br> -e.g:<br>

```
- usage: PyPlaybook.py [-h] -i INPUTFILE [-w W] [-ts TS] [-qs QS] [-delay DELAY<br>
				         [-username USERNAME] [-password PASSWORD]<br>
					 [-secret SECRET] [-v]<br>
- PyPlaybook.py: error: the following arguments are required: -i/--inputfile<br>
'''

* PyPlaybook.py -h	(detailed help)
usage: PyPlaybook.py [-h] -i INPUTFILE [-w W] [-ts TS] [-qs QS] [-delay DELAY]
                     [-username USERNAME] [-password PASSWORD]
                     [-secret SECRET] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputfile INPUTFILE
                        inputfile name is required.
  -w W                  specify if configuration should be save into Startup
                        Config. 'Y' to write config 'N' to preserve Startup
                        Config. If this flag is not specified or any other
                        value is entered the default will be no to write the
                        config changes. Default: 'N'
  -ts TS                Number of Threads to be created. Must be a number from
                        1 thru 100 If a number greater than 50 is entered, the
                        maximum of 100 will be used. Default: '10'
  -qs QS                Queue size. Must be a number from 1 thru 500. If a
                        number greater than 500 is entered, the maximum of 500
                        used. Default: '20'
  -delay DELAY          Delay (1 thru 300) for how long the program waits from
                        device to finish processing the send command before it
                        times out and control is return back to program
                        (delay_factor). If number greater than 300 is entered,
                        the maximum of 300 will be used. Default: '20'
  - outfolder           output folder to save logs to. Will create folder if it doesnt exist.
                        (Default: current folder)
  -username USERNAME    Username to login to the device(s)
  -password PASSWORD    Username password
  -secret SECRET        Device(s) enable secret
  -v, --version         show program's version number and exit

These Python programs will create a '.log' file in the current directory from where the programs are ran. The name of the .log file is automatically generated based on the device name and the IP address of the device.<br> <br> Error handling added to connection object and error loggin added to save error(s) to error.log.<br>

> > > > > > > d6af63c1aa3314c22005ecd2a16f12a0da975372
