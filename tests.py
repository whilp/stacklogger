import inspect
import unittest

from stacklogger import callingframe, srcfile

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

class TestFrameFuncs(unittest.TestCase):
    infokeys = "frame filename lineno function context index".split()
    
    def setUp(self):
        self.frames = dict(function=fake_function())

        fakes = FakeFrames()
        for name in dir(fakes):
            if not name.startswith("fake_"):
                continue
            key = name.replace("fake_", '', 1)
            value = getattr(fakes, name)
            if key not in ("property",):
                value = value()
            self.frames[key] = value

    def callingframe(self, framekey, **expectedkeys):
        result = dict(zip(self.infokeys, callingframe(self.frames[framekey])))
        for k, v in expectedkeys.items():
            if k == "filename":
                self.assertTrue(result[k].endswith(v))
            else:
                self.assertEqual(v, result[k])

    def test_callingframe_function(self):
        self.callingframe("function", 
            filename=__file__,
            function="fake_function")

    def test_callingframe_method(self):
        self.callingframe("method",
            filename="foo",
            function="fake_method")
