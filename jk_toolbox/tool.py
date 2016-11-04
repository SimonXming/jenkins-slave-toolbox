#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json
import threading


class BaseDockerLayerTracer(object):
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

    def handler_stop_status(self, data):
        pass

    def update_trace(self, raw_data):
        data = json.loads(raw_data)
        layer_id = data.get("id", None)
        layer_status = data.get("status", None)
        layer_progress = data.get("progress", None)
        layer_progress_detail = data.get("progressDetail", None)

        if not layer_id or layer_status not in self.TRACE_STATUS:
            self.handler_stop_status(data)
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
                    print("\"status\": {}, \"progress\": {}, \"id\": {}".format(
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

    def stop(self, msg):
        self.pushing_trace.update({"stop": {
            "status": "Error",
            "error": msg,
            "errorDetail": msg,
        }})
