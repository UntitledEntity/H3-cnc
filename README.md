### H3-cnc
[![PY](https://img.shields.io/badge/-PYTHON-000000?style=flat&logo=python)](https://www.python.org/)

A CnC for a server-hopping workspace for penetration-testing.

## FAQ

### How does it work?
It works by reading a list of servers from a text file (servers.txt), and acts as a workspace to use those servers. You can open a remote shell to any server, execute a command on any or all servers, etc. A full list of commands can be viewed typing 'help' or in [this screenshot](https://prnt.sc/atmjEkO-c78u).

## What protocol does it use?
It uses the '[paramiko](https://www.paramiko.org/)' pip module to connect via SSH.

## Formatting
The servers are formatted in any input (command or in servers.txt) as given:
ipv4:user:pass

## License

> Copyright (c) 2022 Jacob Gluska/UntitledEntity

This project is licensed under the [MIT License](https://opensource.org/licenses/mit-license.php) - see the [LICENSE](https://github.com/UntitledEntity/H3-cnc/blob/main/LICENSE) file for details.

### Disclaimer
I am not responsible for anything you do using the code in this repository. This is meant for penetration-testing only, <b>Use only when given permission, or use on your own machines. </b>
