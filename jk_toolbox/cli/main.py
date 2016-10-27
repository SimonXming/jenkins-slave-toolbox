#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys
import logging
import functools
from inspect import getdoc

from .. import __version__
from ..service import Service
from . import signals
from .log_printer import ColoredLogger
from .docopt_command import DocoptDispatcher
from .docopt_command import NoSuchCommand

logging.setLoggerClass(ColoredLogger)
log = logging.getLogger(__name__)
# log.addHandler(logging.StreamHandler())


def main():
    command = dispatch()

    try:
        command()
    except (KeyboardInterrupt, signals.ShutdownException):
        log.error("Aborting.")
        sys.exit(1)
    except Exception as e:
        log.error(e)
        sys.exit(1)


def dispatch():
    dispatcher = DocoptDispatcher(
        TopLevelCommand,
        {'options_first': True, 'version': "0.0.1"})

    try:
        options, handler, command_options = dispatcher.parse(sys.argv[1:])
    except NoSuchCommand as e:
        commands = "\n".join(parse_doc_section("commands:", getdoc(e.supercommand)))
        log.error("No such command: %s\n\n%s", e.command, commands)
        sys.exit(1)

    return functools.partial(perform_command, options, handler, command_options)


def perform_command(options, handler, command_options):
    if options['COMMAND'] in ('help', 'version'):
        # Skip looking up the compose file.
        handler(command_options)
        return

    command = TopLevelCommand(Service)
    handler(command, command_options)


# stolen from docopt master
def parse_doc_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


class TopLevelCommand(object):
    """Define and run multi-container applications with Docker.

    Usage:
      jk-toolbox [options] [COMMAND] [ARGS...]

    Options:
      -v, --version               Print version and exit

    Commands:
      help               Get help on a command
      pull               Pull service images
      push               Push service images
      version            Show the Docker-Compose version information
    """

    def __init__(self, service_class):
        self.service = service_class()

    @classmethod
    def help(cls, options):
        """
        Get help on a command.

        Usage: help [COMMAND]
        """
        if options['COMMAND']:
            subject = get_handler(cls, options['COMMAND'])
        else:
            subject = cls

        print(getdoc(subject))

    def pull(self, options):
        """
        Pull images for services.

        Usage: pull [--username=USERNAME] [--token=TOKEN] [--image_name=IMAGE_NAME]

        Options:
            --username=USERNAME         specify username for pull
            --token=TOKEN               specify token for pull
            --image_name=IMAGE_NAME     specify image name for pull
        """
        username = options("--username", None)
        token = options("--token", None)
        image_name = options.get("--image_name", None)
        if not image_name:
            log.error("Not provide image_name", getdoc(self))

        self.service.docker.pull(
            username=username,
            token=token,
            image_name=image_name,
        )

    def push(self, options):
        """
        Push images for services.

        Usage: push [--username=USERNAME] [--token=TOKEN] [--image_name=IMAGE_NAME]

        Options:
            --username=USERNAME         specify username for pull
            --token=TOKEN               specify token for pull
            --image_name=IMAGE_NAME     specify image name for pull
        """
        username = options("--username", None)
        token = options("--token", None)
        image_name = options.get("--image_name", None)
        if not image_name:
            log.error("Not provide image_name", getdoc(self))

        self.service.docker.push(
            username=username,
            token=token,
            image_name=image_name,
        )

    @classmethod
    def version(cls, options):
        """
        Show version informations

        Usage: version [--short]

        Options:
            --short     Shows only Compose's version number.
        """
        if options['--short']:
            print(__version__)
        else:
            print("0.0.1")
