import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name = "PyPlaybook",
    version = "0.0.4",
    author = "David Morfe",
    author_email = "cybercomprepair@gmail.com",
    license = "MIT",
    description = "SSH/Telnet tool to create log files and to push configuration changes to supported devices.",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dmorfe/playbook_orchestration",
    install_requires = ["netmiko", "pandas", "xlrd", "openpyxl"],
    packages = setuptools.find_packages(),
    py_modules = ["PyPlaybook", "Port_Range_VLAN_changes"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"]
)
