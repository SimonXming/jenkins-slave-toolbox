#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import docker
import threading
from docker.errors import NotFound


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

        for output in self.cli.pull(image_name, stream=True, auth_config=self.docker_auth):
            print(output.strip()[1:-1])

    def push(self, username=None, token=None, image_name=None):
        self.docker_auth.update({
            'username': username,
            'password': '{}{}'.format(self.PREFIX, token)
        })
        if not image_name:
            return
        tracer = LayerTracer()
        try:
            for pull_status in self.cli.push(image_name, stream=True, auth_config=self.docker_auth):
                # print(pull_status.strip()[1:-1])
                tracer.update_trace(pull_status)
            self.cli.remove_image(image_name, force=True)
        except NotFound as e:
            print(e)


class LayerTracer(object):
    """
    实时更新各层的推送情况，但每隔 {PERIOD_SECONDS} 才 print 一次推送状态。
    """
    PERIOD_SECONDS = 2
    TRACE_STATUS = ["Pushing", "Pushed"]
    STOP_STATUS = ["Pushed", "Error"]

    def __init__(self):
        self.pushing_trace = {}
        self.output_trace()

    def _pretty_progress(self, raw_progress):
        if raw_progress:
            return raw_progress.replace("\u003e", ">")
        else:
            return None

    def update_trace(self, raw_data):
        data = json.loads(raw_data)
        layer_id = data.get("id", None)
        layer_status = data.get("status", None)
        layer_progress = data.get("progress", None)
        layer_progress_detail = data.get("progressDetail", None)

        if not layer_id or layer_status not in self.TRACE_STATUS:
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
            self.output_layer_status(data)
        else:
            update_data = {
                layer_id: {
                    "status": layer_status,
                    "progress": self._pretty_progress(layer_progress),
                    "progress_detail": layer_progress_detail
                }
            }
            self.pushing_trace.update(update_data)

    def push_finised(self):
        if not self.pushing_trace:
            return False

        for layer_id, data in self.pushing_trace.iteritems():
            if data.get("status", None) not in self.STOP_STATUS:
                return False
        else:
            return True

    def output_trace(self):
        if self.push_finised():
            pass
        else:
            if self.pushing_trace:
                for layer_id, data in self.pushing_trace.iteritems():
                    print("status: {}, progress: {}, id: {}".format(
                        data.get("status", ""),
                        self._pretty_progress(data.get("progress", "")),
                        layer_id
                    ))
            threading.Timer(self.PERIOD_SECONDS, self.output_trace).start()

    def output_layer_status(self, data):
        output = ""
        for key, val in data.iteritems():
            output += "\"{}\": {}, ".format(key, val)
        print(output)
