#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: srv_gui.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: GUI service
"""

import logging
import threading

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gio

from basico.core.srv import Service
from basico.core.win import GtkAppWindow
from basico.core.env import FILE


class UIApp(Gtk.Application):
    """
    Missing class docstring (missing-docstring)
    """
    uiapp = None
    window = None

    def __init__(self, *args, **kwargs):
        """
        Missing method docstring (missing-docstring)
        """
        super().__init__(application_id="net.t00mlabs.basico", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.app = args[0]
        GLib.set_application_name("Basico")
        GLib.set_prgname('basico')
        self.log = logging.getLogger('UIApp')
        self.log.addHandler(self.app.intercepter)
        # ~ self.connect_signals()
        self.get_services()


    # ~ def setup_signals(self, *args):
        # ~ GObject.signal_new('activate-focus', UIApp, GObject.SignalFlags.RUN_LAST, None, () )
        # ~ GObject.signal_new('gui-started', UIApp, GObject.SignalFlags.RUN_LAST, None, () )

    def do_activate(self):
        # DOC: https://wiki.gnome.org/HowDoI/GtkApplication
        # https://stackoverflow.com/questions/41883527/uniqueness-of-gtk-application-without-creating-any-window
        # ~ self.emit('gui-started', self.connect_signals)
        if not hasattr(self, "my_app_settings"):
            self.hold()
            self.my_app_settings = "Primary application instance."
            self.window = self.srvgui.add_widget('gtk_app_window_main', GtkAppWindow(self))
            self.window.connect("delete-event", self.srvgui.quit)
            self.window.connect("key-press-event",self.on_key_press_event)
            self.log.debug("New Basico instance created")
            # ~ self.srvuif.statusbar_msg("Welcome to Basico", True)
        else:
            self.log.debug("Basico is already running!")
        splash = self.app.get_splash()
        splash.hide()
        # ~ self.setup_signals()
        # ~ self.emit('gui-started')
        self.th = threading.Thread(name='statusbar', target=self.srvclb.gui_statusbar_update)
        self.th.setDaemon(True)
        self.th.start()
        # ~ self.emit('gui-started', self.connect_signals)

    def on_key_press_event(self, widget, event):
        if Gdk.keyval_name(event.keyval) == 'Escape':
            # ~ self.srvclb.action_annotation_cancel()
            pass

    def update(self, *args):
        self.uiapp.emit('gui-update')

    def get_services(self):
        """
        Missing method docstring (missing-docstring)
        """
        self.srvgui = self.app.get_service('GUI')
        self.srvclb = self.app.get_service('Callbacks')
        self.srvuif = self.app.get_service('UIF')


    def get_window(self):
        """
        Missing method docstring (missing-docstring)
        """
        return self.window


    def get_controller(self):
        """
        Missing method docstring (missing-docstring)
        """
        return self.app


class GUI(Service):
    """
    Missing class docstring (missing-docstring)
    """
    uiapp = None
    srvsap = None
    widgets = {} # Widget name : Object
    keys = {} # Key : Value; keys: doctype, property, values
    signals = {} # Signals dictionary for all widgets (widget::signal)

    def initialize(self):
        """
        Setup GUI Service
        """

    def run(self):
        """
        Let GUI service start
        """
        GObject.threads_init()
        self.uiapp = UIApp(self.app)
        self.log.debug("Setting up GUI")
        # ~ GObject.signal_new('gui-started', self.uiapp, GObject.SignalFlags.RUN_LAST, None, () )
        GObject.signal_new('gui-started', self.uiapp, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        self.uiapp.run()

    def get_uiapp(self):
        self.log.debug(self.uiapp)
        return self.uiapp

    def quit(self, window, event):
        """
        GUI destroyed
        """
        self.app.stop()


    def end(self):
        """
        End GUI Service
        """
        self.uiapp.quit()
        self.log.debug("GUI terminated")


    def swap_widget(self, parent, widget):
        """
        Swap widget inside a container
        """
        try:
            child = parent.get_children()[0]
            parent.remove(child)
            parent.add(widget)
        except IndexError:
            parent.add(widget)
        except Exception:
            self.print_traceback()
            raise

        widget.show_all()


    def get_keys(self):
        return self.keys


    def get_keys_starting_with(self, name):
        matches = []
        for key in self.keys:
            if key.startswith(name):
                matches.append(key)

        return matches


    def get_key_value(self, key):
        """
        Return current value from var cache
        """
        return self.keys[key]


    def set_key_value(self, key, value):
        """
        Set current value for var cache
        """
        self.keys[key] = value


    def add_signal(self, widget, signal, value):
        """
        Add signal to signals cache
        """
        signal_name = "%s::%s" % (widget, signal)
        self.signals[signal_name] = value


    def get_signal(self, widget, signal):
        """
        Return signal from cache
        """
        signal_name = "%s::%s" % (widget, signal)
        try:
            return self.signals[signal_name]
        except KeyError:
            return None


    def add_widget(self, name, obj=None):
        """
        Add widget to cache
        """
        if obj is not None:
            self.widgets[name] = obj

        return obj


    def get_widget(self, name):
        """
        Return widget from cache
        """
        try:
            return self.widgets[name]
        except KeyError as warning:
            # ~ self.log.warning(warning)
            self.log.error(self.get_traceback())
            raise
            return None


    def get_widgets(self):
        """
        Missing method docstring (missing-docstring)
        """
        return self.widgets


    def get_app(self):
        """
        Missing method docstring (missing-docstring)
        """
        return self.uiapp


    def get_window(self):
        """
        Missing method docstring (missing-docstring)
        """
        return self.uiapp.get_window()