#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from .docker import DockerService


class Service(object):
    def __init__(self):
        self.docker = DockerService()
