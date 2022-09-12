import pytest
from typing import Any
from src.listener import Listener

class MockCallback:
    @staticmethod
    def routing_key():
        return "routing_key"

def test_listener_with_event_name():
    Listener.on('event_name..blalala', lambda x: print(x))

def test_listener_with_no_event_name():
   with pytest.raises(ValueError):
        Listener.on(None, lambda x: print(x))

def test_listener_with_wrong_pattern_event_name():
   with pytest.raises(ValueError):
        Listener.on("wrong.test", lambda x: print(x))

def test_listener_with_event_parts_name_with_all():
    l = Listener.on('payment.payments.pay')
    assert l.event_name == 'payment.payments.pay.all'

def test_listener_with_callback_none():
    l = Listener.on(event_name='payment.payments.pay.all', callback=None)
    assert l.callback is not None
    l.callback(None, MockCallback, None, {'body': 'example'})

def test_listener_callback_not_none():
    l = Listener.on(event_name='payment.payments.pay.all', callback=lambda x: print('testing', x))
    l.callback(10)
