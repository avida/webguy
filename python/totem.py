#!/usr/bin/python3
import dbus
for service in dbus.SystemBus().list_names():
    print(service)
T_SERVICE_NAME = 'org.mpris.Totem'
T_OBJECT_PATH = '/Player'
T_INTERFACE = 'org.freedesktop.MediaPlayer'
session_bus = dbus.SessionBus()
totem = session_bus.get_object(T_SERVICE_NAME, T_OBJECT_PATH)
totem_mediaplayer = dbus.Interface(totem, dbus_interface=T_INTERFACE)
print(totem_mediaplayer.GetStatus()[0])
