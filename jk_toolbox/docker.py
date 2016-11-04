#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import docker
from docker.errors import NotFound

from .tool import BaseDockerLayerTracer


class PullLayerTracer(BaseDockerLayerTracer):
    """
    实时更新各层的推送情况，但每隔 {PERIOD_SECONDS} 才 print 一次推送状态。
    """
    PERIOD_SECONDS = 2
    TRACE_STATUS = ["Downloading", "Extracting", "Pull complete"]
    STOP_STATUS = ["Pull complete", "Error"]

    def handler_stop_status(self, data):
        if data.get("error", None):
            self.pushing_trace.update({"all_layers": {
                "status": "Error",
                "error": data.get("error", None),
                "errorDetail": data.get("errorDetail", None),
            }})
        if "Status: Downloaded" in data.get("status", None):
            self.pushing_trace.update({"all_layers": {
                "status": "Pull complete"
            }})
        if "Status: Image is up to date" in data.get("status", None):
            self.pushing_trace.update({"all_layers": {
                "status": "Pull complete"
            }})


class PushLayerTracer(BaseDockerLayerTracer):
    """
    实时更新各层的推送情况，但每隔 {PERIOD_SECONDS} 才 print 一次推送状态。
    """
    PERIOD_SECONDS = 2
    TRACE_STATUS = ["Pushing", "Pushed"]
    STOP_STATUS = ["Pushed", "Error"]

    def handler_stop_status(self, data):
        if data.get("error", None):
            self.pushing_trace.update({"all_layers": {
                "status": "Error",
                "error": data.get("error", None),
                "errorDetail": data.get("errorDetail", None),
            }})
        if data.get("aux", None):
            self.pushing_trace.update({"all_layers": {
                "status": "Pushed"
            }})


class DockerService(object):
    def __init__(self, base_url="unix:///var/run/docker.sock"):
        self.PREFIX = 'hack-token'
        self.cli = docker.Client(base_url=base_url)
        self.docker_auth = {
            'username': "",
            'password': ""
        }

    def pull(self, username=None, token=None, image_name=None):
        self.docker_auth.update({
            'username': username,
            'password': '{}{}'.format(self.PREFIX, token)
        })

        if not image_name:
            return

        tracer = PullLayerTracer()
        try:
            for pull_status in self.cli.pull(image_name, stream=True, auth_config=self.docker_auth):
                # print(output.strip()[1:-1])
                tracer.update_trace(pull_status)
        except Exception as e:
            tracer.stop(e)
            print(e)

    def push(self, username=None, token=None, image_name=None):
        self.docker_auth.update({
            'username': username,
            'password': '{}{}'.format(self.PREFIX, token)
        })
        if not image_name:
            return

        tracer = PushLayerTracer()
        try:
            for push_status in self.cli.push(image_name, stream=True, auth_config=self.docker_auth):
                # print(pull_status.strip()[1:-1])
                tracer.update_trace(push_status)
            self.cli.remove_image(image_name, force=True)
        except NotFound as e:
            tracer.stop(e)
            print(e)
        except Exception as e:
            tracer.stop(e)
            print(e)
