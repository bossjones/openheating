from openheating.tests.switches import TestSwitch


from openheating.polling import Poller
from openheating.thermometer_dummy import DummyThermometer
from openheating.source import Source
from openheating.sink import Sink
from openheating.hysteresis import Hysteresis
from openheating.transport import Transport

import unittest
import logging

class TransportBasicTest(unittest.TestCase):
    def test__basic(self):
        poller = Poller()
        
        sink_thermometer = DummyThermometer(initial_temperature=20)
        sink = Sink(name='my-sink', thermometer=sink_thermometer,
                    hysteresis=Hysteresis(33, 47))
        poller.add(sink)

        source_thermometer = DummyThermometer(initial_temperature=80)
        source = Source(name='my-source', thermometer=source_thermometer)

        pump_switch = TestSwitch(on=False)
        transport = Transport(name='my-transport', source=source, sink=sink,
                              diff_hysteresis=Hysteresis(0, 5),
                              pump_switch=pump_switch)
        poller.add(transport)

        # pump is off initially. switched on after first move, due to
        # difference of 60 degrees. sink is far below its desired
        # temperature, so it explicitly requests heating
        if True:
            self.assertFalse(pump_switch.is_on())
            poller.poll('initial, diff is huge, request')
            self.assertTrue(pump_switch.is_on())
            self.assertIn(sink, source.requesters())

        # sink reaches its desired temperature. pump is kept running
        # nonetheless - it's the temperature difference which
        # matters. no heating explicitly requested anymore though.
        if True:
            sink_thermometer.set_temperature(50)
            poller.poll('sink satisfied, diff still there')
            self.assertTrue(pump_switch.is_on())
            self.assertNotIn(sink, source.requesters())

        # source's temperature falls to 55.1. this makes a temperature
        # difference of 5.1. threshold is 5, so pump is kept running.
        if True:
            source_thermometer.set_temperature(55.1)
            poller.poll('source cools, still some diff')
            self.assertTrue(pump_switch.is_on())
            self.assertNotIn(sink, source.requesters())
            
        # source's temperature down to 52. still a difference of 2,
        # which makes us not switch off the pump.
        if True:
            source_thermometer.set_temperature(52)
            poller.poll('source cools even more, still some diff')
            self.assertTrue(pump_switch.is_on())
            self.assertNotIn(sink, source.requesters())

        # sink at 50, source falls down to 49.9. negative difference
        # -> pump off.
        if True:
            source_thermometer.set_temperature(49.9)
            poller.poll('negative diff')
            self.assertFalse(pump_switch.is_on())
            self.assertNotIn(sink, source.requesters())

        # sink cools down to 33.1. pump on due to huge difference. no
        # request though because 33.1 is well between sink's
        # hysteresis.
        if True:
            sink_thermometer.set_temperature(33.1)
            poller.poll()
            self.assertTrue(pump_switch.is_on())
            self.assertNotIn(sink, source.requesters())

        # sink cools down to 32.9 -> request heating
        if True:
            sink_thermometer.set_temperature(32.9)
            poller.poll()
            self.assertTrue(pump_switch.is_on())
            self.assertIn(sink, source.requesters())

    @unittest.skip("jjj")
    def test_restart_delay(self):
        '''
        Consumer is satisfied with its temperature, pump not running
        initially. consumer's temperature falls, say, 1 degree below
        wanted, pump *not* switched on immediately.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=40)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=80),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()
        self.failIf(pump_switch.is_on())

        consumer.set_temperature(39)
        transport.poll()
        self.failIf(pump_switch.is_on())

    @unittest.skip("jjj")
    def test__producer_below_wanted_but_pays_off(self):
        '''
        Producer's temperature is well below consumer's wanted temperature,
        but we take what we can get.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=28),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=5, range_high=5, pump_switch=pump_switch)

        transport.poll()

        self.failUnless(pump_switch.is_on())

    @unittest.skip("jjj")
    def test__producer_below_wanted_but_doesnt_pay_off(self):
        '''
        Producer's temperature is well below consumer's wanted
        temperature, and it does not pay off to take this small amount
        of temperature.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=21),
                            overheat_temperature=100, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()

        self.failIf(pump_switch.is_on())

    @unittest.skip("jjj")
    def test__producer_has_nothing__pump_not_initially_running(self):
        '''
        Consumer is unsatisfied. producer has nothing to satisfy
        him. pump *is not* initially running, and *is not* switched
        on.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=20),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()
        self.failIf(pump_switch.is_on())

    @unittest.skip("jjj")
    def test__producer_has_nothing__pump_initially_running(self):
        '''
        Consumer is unsatisfied. producer has nothing to satisfy
        him. pump *is* initially running, and *is switched off*.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=20),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=True)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()
        self.failIf(pump_switch.is_on())

class TransportAcquireReleaseProducerTest(unittest.TestCase):
    '''
    Transport coordinates between consumer's needs and a producer.
    It can peek the producer to make some temperature if the consumer needs it.
    '''
    
    @unittest.skip("jjj")
    def test__producer_not_acquired_when_consumer_satisfied(self):
        '''
        Simplest thing: when nobody needs anything,
        then we don't produce
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=48)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=20),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()

        self.failIf(producer.is_acquired())
        
    @unittest.skip("jjj")
    def test__producer_not_acquired_when_producer_has_enough_temperature(self):
        '''
        Producer's temperature is enough to satisfy consumer.
        Producer not acquired.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = Producer(name='Producer', backend=TestProducerBackend(initial_temperature=80),
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()

        self.failIf(producer.is_acquired())
        
    @unittest.skip("jjj")
    def test__producer_acquired_when_consumer_not_satisfied(self):
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=30)
        producer_backend = TestProducerBackend(initial_temperature=20)
        producer = Producer(name='Producer', backend=producer_backend,
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))
        pump_switch = TestSwitch(on=False)
        transport = Transport(name='xxx', producer=producer, consumer=consumer, range_low=7, range_high=7, pump_switch=pump_switch)

        transport.poll()

        self.failIf(pump_switch.is_on())
        self.failUnless(producer.is_acquired())

        producer_backend.set_temperature(70)

        transport.poll()

        self.failUnless(pump_switch.is_on())
        self.failUnless(producer.is_acquired())

        consumer.set_temperature(47)

        transport.poll()

        self.failIf(pump_switch.is_on())
        self.failIf(producer.is_acquired())

    @unittest.skip("jjj")
    def test__producer_with_two_consumers__synchronous(self):
        '''
        Two consumers are attached to a producer. Both consumers
        reach their desired temperature level at the same time.
        '''

        producer_backend = TestProducerBackend(initial_temperature=20)
        producer = Producer(name='Producer', backend=producer_backend,
                            overheat_temperature=1000, alarm_switch=TestSwitch(on=False))

        consumerA = TestConsumer(wanted_temperature=40, initial_temperature=30)
        pumpA = TestSwitch(on=False)
        transportA = Transport(name='Transport-A', producer=producer, consumer=consumerA, range_low=7, range_high=7, pump_switch=pumpA)

        consumerB = TestConsumer(wanted_temperature=40, initial_temperature=30)
        pumpB = TestSwitch(on=False)
        transportB = Transport(name='Transport-B', producer=producer, consumer=consumerB, range_low=7, range_high=7, pump_switch=pumpB)

        transportA.poll()
        transportB.poll()

        # not yet hot enough ...
        self.failIf(pumpA.is_on())
        self.failIf(pumpB.is_on())

        # ... though heat is underway
        self.failUnless(producer.is_acquired())

        # heat is coming
        producer_backend.set_temperature(70)

        transportA.poll()
        transportB.poll()

        self.failUnless(pumpA.is_on())
        self.failUnless(pumpB.is_on())
        self.failUnless(producer.is_acquired())

        consumerA.set_temperature(47)
        consumerB.set_temperature(47)

        transportA.poll()
        transportB.poll()

        self.failIf(pumpA.is_on())
        self.failIf(pumpB.is_on())
        self.failIf(producer.is_acquired())

    @unittest.skip("jjj")
    def test__producer_with_two_consumers__asynchronous(self):
        '''
        Two consumers are attached to a producer. One consumer reaches
        its temperature level, while the other keeps wanting.
        '''

        producer_backend = TestProducerBackend(initial_temperature=20)
        producer = Producer(name='Producer', backend=producer_backend, overheat_temperature=1000, alarm_switch=TestSwitch(on=False))

        consumerA = TestConsumer(wanted_temperature=40, initial_temperature=30)
        pumpA = TestSwitch(on=False)
        transportA = Transport(name='Transport-A', producer=producer, consumer=consumerA, range_low=7, range_high=7, pump_switch=pumpA)

        consumerB = TestConsumer(wanted_temperature=40, initial_temperature=30)
        pumpB = TestSwitch(on=False)
        transportB = Transport(name='Transport-B', producer=producer, consumer=consumerB, range_low=7, range_high=7, pump_switch=pumpB)

        transportA.poll()
        transportB.poll()

        # not yet hot enough ...
        self.failIf(pumpA.is_on())
        self.failIf(pumpB.is_on())

        # ... though heat is underway
        self.failUnless(producer.is_acquired())
        self.failUnless(len(producer.get_acquirers()) == 2)
        self.failUnless('Transport-A' in producer.get_acquirers())
        self.failUnless('Transport-B' in producer.get_acquirers())

        # heat is coming
        producer_backend.set_temperature(70)

        transportA.poll()
        transportB.poll()

        self.failUnless(pumpA.is_on())
        self.failUnless(pumpB.is_on())
        self.failUnless(producer.is_acquired())
        self.failUnless(len(producer.get_acquirers()) == 2)
        self.failUnless('Transport-A' in producer.get_acquirers())
        self.failUnless('Transport-B' in producer.get_acquirers())

        # A is satisfied
        consumerA.set_temperature(47)

        transportA.poll()
        transportB.poll()

        # A down, B still wants more
        self.failIf(pumpA.is_on())
        self.failUnless(pumpB.is_on())
        self.failUnless(producer.is_acquired())
        self.failUnless(len(producer.get_acquirers()) == 1)
        self.failUnless('Transport-B' in producer.get_acquirers())

suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransportBasicTest))
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransportAcquireReleaseProducerTest))

# suite.addTest(TransportBasicTest("test__pump_on_off_simple"))
# suite.addTest(TransportPeeksProducerTest("test__producer_not_peeked_when_consumer_satisfied"))

# logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
