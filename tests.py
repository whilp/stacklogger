import inspect
import unittest

from stacklogger import srcfile

currentframe = inspect.currentframe

class FakeFrames(object):
    
    def fake_method(self):
        return currentframe()
    
    @property
    def fake_property(self):
        return currentframe()

    @classmethod
    def fake_classmethod(cls):
        return currentframe()

    @staticmethod
    def fake_staticmethod():
        return currentframe()

def fake_function():
    return currentframe()

class TestUtils(unittest.TestCase):
    
    def test_srcfile(self):
        self.assertTrue(srcfile("foo.py").endswith("foo.py"))
        self.assertTrue(srcfile("foo.pyc").endswith("foo.py"))
        self.assertTrue(srcfile("foo.pyo").endswith("foo.py"))
        self.assertTrue(srcfile("foo").endswith("foo"))
