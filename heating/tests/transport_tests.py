from heating.tests.producers import TestProducer
from heating.tests.consumers import TestConsumer
from heating.tests.pumps import TestPump

from heating.control.transport import Transport

import unittest

class TransportBasicTest(unittest.TestCase):
    def test_pump_on_off_simple(self):
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=80)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        # pump is off initially. switched on after first move, due to
        # difference of 40 degrees.
        self.failIf(pump.is_running())
        transport.move()
        self.failUnless(pump.is_running())

        # consumer reaches temperature, pump switched off
        consumer.set_temperature(40)
        transport.move()
        self.failIf(pump.is_running())

        # consumer's temperature falls by a lot of degrees (20 is a
        # lot), pump switched on again.
        consumer.set_temperature(20)        
        transport.move()
        self.failUnless(pump.is_running())

        # rises right below wanted, pump still running
        consumer.set_temperature(39)
        transport.move()
        self.failUnless(pump.is_running())

    def test_restart_delay(self):
        '''
        Consumer is satisfied with its temperature, pump not running
        initially. consumer's temperature falls, say, 1 degree below
        wanted, pump *not* switched on immediately.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=40)
        producer = TestProducer(initial_temperature=80)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()
        self.failIf(pump.is_running())

        consumer.set_temperature(39)
        transport.move()
        self.failIf(pump.is_running())

    def test__producer_below_wanted_but_pays_off(self):
        '''
        Producer's temperature is well below consumer's wanted temperature,
        but we take what we can get.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=28)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()

        self.failUnless(pump.is_running())

    def test__producer_below_wanted_but_doesnt_pay_off(self):
        '''
        Producer's temperature is well below consumer's wanted temperature,
        and it does not pay off to take this small amount of temperature.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=21)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()

        self.failIf(pump.is_running())

    def test__producer_has_nothing__pump_not_initially_running(self):
        '''
        Consumer is unsatisfied. producer has nothing to satisfy
        him. pump *is not* initially running, and *is not* switched
        on.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=20)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()
        self.failIf(pump.is_running())

    def test__producer_has_nothing__pump_initially_running(self):
        '''
        Consumer is unsatisfied. producer has nothing to satisfy
        him. pump *is* initially running, and *is switched off*.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=20)
        pump = TestPump(running=True)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()
        self.failIf(pump.is_running())

class TransportPeeksProducerTest(unittest.TestCase):
    '''
    Transport coordinates between consumer's needs and a producer.
    It can peek the producer to make some temperature if the consumer needs it.
    '''
    
    def test__producer_not_peeked_when_consumer_satisfied(self):
        '''
        Simplest thing: when nobody needs anything,
        then we don't produce
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=40)
        producer = TestProducer(initial_temperature=20)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()

        self.failIf(producer.peeked())
        
    def test__producer_not_peeked_when_producer_has_enough_temperature(self):
        '''
        Producer's temperature is enough to satisfy consumer.
        Producer not peeked.
        '''
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=20)
        producer = TestProducer(initial_temperature=80)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()

        self.failIf(producer.peeked())
        
    def test__producer_peeked_when_consumer_not_satisfied(self):
        consumer = TestConsumer(wanted_temperature=40, initial_temperature=30)
        producer = TestProducer(initial_temperature=20)
        pump = TestPump(running=False)
        transport = Transport(producer=producer, consumer=consumer, anti_oscillating_threshold=7, pump=pump)

        transport.move()

        self.failIf(pump.is_running())
        self.failUnless(producer.peeked())
        
suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransportBasicTest))
suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransportPeeksProducerTest))

#suite.addTest(TransportPeekTest("test__producer_peeked_when_consumer_not_satisfied"))

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
