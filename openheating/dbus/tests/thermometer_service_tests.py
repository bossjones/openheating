from openheating.testutils.thermometer import TestThermometer
from openheating.hardware.thermometer_hwmon import HWMON_I2C_Thermometer
from openheating.dbus.thermometer_service_config import ThermometerServiceConfig

import unittest

class ThermometerServiceTest(unittest.TestCase):
    def test__configfile(self):
        content = '\n'.join(
            ['DAEMON_ADDRESS = "tcp:host=1.2.3.4,port=6666"',
             'BUS_NAME = "some.arbitrary.name"',
             'PARENT_PATH = "/my/thermometers"',

             'THERMOMETERS = (',
             '    ("name_1", HWMON_I2C_Thermometer(bus_number=1, address=0x49)),',
             '    ("name_2", HWMON_I2C_Thermometer(bus_number=1, address=0x4a)),',
             '    ("name_3", TestThermometer(initial_temperature=4.5)),',
             ')',
             ])
        
        config = ThermometerServiceConfig(content)

        self.failUnlessEqual(config.daemon_address(), "tcp:host=1.2.3.4,port=6666")
        self.failUnlessEqual(config.bus_name(), "some.arbitrary.name")

        self.failUnlessEqual(config.thermometers()[0]['object_path'], '/my/thermometers/name_1')
        self.failUnless(isinstance(config.thermometers()[0]['thermometer'], HWMON_I2C_Thermometer))
        self.failUnlessEqual(config.thermometers()[0]['thermometer'].bus_number(), 1)
        self.failUnlessEqual(config.thermometers()[0]['thermometer'].address(), 0x49)

        self.failUnlessEqual(config.thermometers()[1]['object_path'], '/my/thermometers/name_2')
        self.failUnless(isinstance(config.thermometers()[1]['thermometer'], HWMON_I2C_Thermometer))
        self.failUnlessEqual(config.thermometers()[1]['thermometer'].bus_number(), 1)
        self.failUnlessEqual(config.thermometers()[1]['thermometer'].address(), 0x4a)
 
        self.failUnlessEqual(config.thermometers()[2]['object_path'], '/my/thermometers/name_3')
        self.failUnless(isinstance(config.thermometers()[2]['thermometer'], TestThermometer))
        self.failUnlessAlmostEqual(config.thermometers()[2]['thermometer'].temperature(), 4.5)

suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ThermometerServiceTest))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
    