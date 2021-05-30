import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
    name = "PyPlaybook",
    version = "0.0.2",
    author = "David Morfe",
    author_email = "morphetech@gmail.com",
    license = "MIT",
    description = "Python tool to automate connecting to network devices and retrieve information and/or make configration changes",
    long_description=long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dmorfe/playbook_orchestration",
    install_requires = ["netmiko", "pandas"],
    packages = setuptools.find_packages(),
    py_modules = ["PyPlaybook", "Port Range VLAN changes"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"]
)
