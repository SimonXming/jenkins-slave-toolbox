"""Define and run multi-container applications with Docker.

Usage:
  jk-toolbox [COMMAND] [ARGS...]

Commands:
  help               Get help on a command
  pull               Pull service images
  push               Push service images
  version            Show the Docker-Compose version information
"""
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)
