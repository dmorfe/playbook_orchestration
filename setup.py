import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name = "PyPlaybook",
    version = "0.0.7",
    author = "David Morfe",
    author_email = "cybercomprepair@gmail.com",
    license = "MIT",
    description = "SSH/Telnet/playbook/automation tool/configuration tool/push commands from excel",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dmorfe/playbook_orchestration",
    install_requires = ["netmiko", "pandas", "xlrd", "openpyxl"],
    packages = setuptools.find_packages(),
    py_modules = ["PyPlaybook"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"]
)
