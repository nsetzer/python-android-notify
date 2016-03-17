#! /usr/bin/python2.7

import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger
from kivy.lib import osc
from kivy.clock import Clock

from plyer import notification
from plyer.utils import platform
from plyer.compat import PY2

import sys
from subprocess import Popen

# Todo pull these alues from a file common to main application and service
hostname = '127.0.0.1'
serviceport = 15123
activityport = 15124

class NotificationDemo(BoxLayout):

    def do_notify(self, mode='normal'):
        """ collect text edit text and send to the background service """

        title = self.ids.notification_title.text
        message = self.ids.notification_text.text

        if PY2:
            title = title.decode('utf8')
            message = message.decode('utf8')

        osc.sendMsg('/update', dataArray=(title,message,), port=serviceport)

class NotificationDemoApp(App):
    def build(self):

        self.start_service()

        return NotificationDemo()

    def __init__(self,**kwargs):
        super(NotificationDemoApp,self).__init__(**kwargs)
        self.pid = None # popen service reference
        self.service = None # android service reference

    def start_service(self):

        if platform == "android":
            Logger.info("main: Creating Android Service")
            from android import AndroidService
            service = AndroidService('Notification Demo', 'running')
            service.start('service started')
            self.service = service
        else:
            # purely for testing on non-android platforms,
            # although notification will not work
            Logger.info("main: Creating Service as Secondary Process")
            self.pid = Popen([sys.executable, "service/main.py"])

        osc.init()
        oscid = osc.listen(ipAddr=hostname, port=activityport)

        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)

    def stop_service(self):
        if self.pid is not None:
            Logger.info("main: stopping popen process")
            self.pid.kill()
        if self.service is not None:
            Logger.info("main: stopping android service")
            self.service.stop()
            self.service = None

    def on_stop(self):
        self.stop_service()
        Logger.critical('main: exit')

if __name__ == '__main__':
    NotificationDemoApp().run()

