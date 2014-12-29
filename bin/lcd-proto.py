#!/usr/bin/python3

from openheating.thermometer_manager import ThermometerManager
from openheating.hd44780 import HD44780_LCD
from openheating.dbus.thermometer import DBusThermometer
from openheating.error import HeatingException

import dbus.bus
import time
from datetime import datetime

connection = dbus.bus.BusConnection('tcp:host=192.168.1.11,port=6666')
display = HD44780_LCD(
    rs=27,
    en=22,
    d4=25,
    d5=24,
    d6=23,
    d7=18, 
    cols=20,
    lines=4)

thermo_mgr = ThermometerManager((
        ('boiler-top', DBusThermometer(connection=connection, name='org.openheating.boiler', path='/thermometers/top')),
        ('boiler-middle', DBusThermometer(connection=connection, name='org.openheating.boiler', path='/thermometers/middle')),
        ('boiler-bottom', DBusThermometer(connection=connection, name='org.openheating.boiler', path='/thermometers/bottom')),
        ('hk-vl', DBusThermometer(connection=connection, name='org.openheating.heizraum', path='/thermometers/heizkreis_vl')),
        ('boiler-vl', DBusThermometer(connection=connection, name='org.openheating.heizraum', path='/thermometers/boiler_vl')),
        ('ofen-vl', DBusThermometer(connection=connection, name='org.openheating.heizraum', path='/thermometers/ofen_vl')),
        ('ofen', DBusThermometer(connection=connection, name='org.openheating.ofen', path='/thermometers/ofen')),
        ))

boiler_top = thermo_mgr.create_proxy_thermometer('boiler-top')
boiler_middle = thermo_mgr.create_proxy_thermometer('boiler-middle')
boiler_bottom = thermo_mgr.create_proxy_thermometer('boiler-bottom')
hk_vl = thermo_mgr.create_proxy_thermometer('hk-vl')
boiler_vl = thermo_mgr.create_proxy_thermometer('boiler-vl')
ofen_vl = thermo_mgr.create_proxy_thermometer('ofen-vl')
ofen = thermo_mgr.create_proxy_thermometer('ofen')

def get_temperature(thermometer):
    try:
        return '%.1f' % thermometer.temperature()
    except HeatingException:
        return 'ERR!'

while True:
    temps = {
        'now': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'boiler-top': get_temperature(boiler_top),
        'boiler-middle': get_temperature(boiler_middle),
        'boiler-bottom': get_temperature(boiler_bottom),
        'hk-vl': get_temperature(hk_vl),
        'boiler-vl': get_temperature(boiler_vl),
        'ofen-vl': get_temperature(ofen_vl),
        'ofen': get_temperature(ofen),
        }
    msg = \
        ('%(now)s\n' + \
         'Boi:%(boiler-top)s/%(boiler-middle)s/%(boiler-bottom)s\n' + \
         'HK:%(hk-vl)s,WW:%(boiler-vl)s\n' + \
         'Ofen:%(ofen)s,VL:%(ofen-vl)s') % temps

    print(msg+'\n--')

    display.clear()
    display.message(msg)
    time.sleep(15)
