#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_driver.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Selenium Driver service
"""

import os
import sys
import time
import logging
from enum import IntEnum
import threading
import queue
import time

from gi.repository import GObject
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as SeleniumService
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from basico.core.mod_env import LPATH, FILE
from basico.core.mod_srv import Service

# Disable logging for imported modules
# Comment to see what is going on behind the scenes
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium').setLevel(logging.WARNING)
# ~ logging.getLogger("WDM").setLevel(logging.ERROR)
# ~ logging.getLogger('webdriver_manager').setLevel(logging.ERROR)
# ~ logging.getLogger('GeckoDriverManager').setLevel(logging.ERROR)

# GECKODRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz"

TIMEOUT = 3

class DriverStatus(IntEnum):
    STOPPED = 0 # Webdriver not loaded
    WAITING = 1 # Webdriver loaded. Waiting for a request
    RUNNING = 2 # Webdriver executing a request
    DISABLE = 3 # Webdriver broken!


class DownloadManager(Service):
    queue = queue.Queue()
    retry = 0
    driver = None
    driver_status = DriverStatus.STOPPED
    url_sid = None
    url_uri = None
    url_type = None

    def initialize(self):
        GObject.signal_new('download-complete', DownloadManager, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        threading.Thread(target=self.download, daemon=True).start()
        self.log.debug("Basico Download Manager started")

    def __set_driver(self, driver):
        self.driver = driver

    def get_driver(self):
        return self.driver

    def __set_driver_status(self, status):
        self.driver_status = status

    def get_driver_status(self):
        return self.driver_status

    def get_url_uri(self):
        return self.url_uri

    def get_url_type(self):
        return self.url_type

    def request(self, url_sid, url_uri, url_type):
        self.url_sid = url_sid
        self.url_uri = url_uri
        self.url_type = url_type
        self.queue.put(url_uri)

    def download(self):
        while True:
            url = self.queue.get()
            self.log.debug("Downloading %s", url)
            if self.retry > 2:
                self.__set_driver_status(DriverStatus.DISABLE)

            status = self.get_driver_status()
            self.log.debug("WebDriver status: %s", status)

            if status == DriverStatus.DISABLE:
                self.log.error("Webdriver not working anymore")
                return None

            while status == DriverStatus.RUNNING:
                time.sleep(1)
                status = self.get_driver_status()

            if status == DriverStatus.STOPPED:
                try:
                    options = Options()
                    options.profile = LPATH['FIREFOX_PROFILE']
                    options.headless = True
                    GDM = GeckoDriverManager(log_level=logging.ERROR)
                    service = SeleniumService(executable_path=GDM.install())
                    driver = webdriver.Firefox(options=options, service=service)
                    self.__set_driver_status(DriverStatus.WAITING)
                    self.__set_driver(driver)
                    self.log.debug("New webdriver instance created and ready")
                except Exception as error:
                    self.__set_driver_status(DriverStatus.STOPPED)
                    self.log.error(error)
                    self.retry += 1
                    self.request(self.url)

            status = self.get_driver_status()
            if status == DriverStatus.WAITING:
                self.__set_driver_status(DriverStatus.RUNNING)
                try:
                    driver = self.get_driver()
                    driver.get(url)
                    element_present = EC.presence_of_element_located((By.ID, 'content'))
                    WebDriverWait(driver, TIMEOUT).until(element_present)
                except TimeoutException:
                    self.__set_driver_status(DriverStatus.WAITING)
                except Exception as error:
                    self.log.error(error)
                    self.retry += 1
                    self.__set_driver_status(DriverStatus.STOPPED)
                    self.request(url)
                finally:
                    self.log.debug("SAP Note downloaded")
                    self.retry = 0
                    self.__set_driver_status(DriverStatus.WAITING)
                    self.emit('download-complete', (self.url_sid, self.url_type))
            self.queue.task_done()

    def end(self):
        self.queue.join()
        driver = self.get_driver()
        if driver is not None:
            driver.quit()
            self.__set_driver(None)
        self.log.debug("Basico Download Manager stopped")
