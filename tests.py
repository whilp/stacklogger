import inspect
import logging
import logging.handlers
import os
import unittest

from stacklogger import callingframe, framefunc, srcfile

currentframe = inspect.currentframe

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        
        def emit(self, record):
            pass

logging.getLogger("fakes").addHandler(NullHandler())

NoDefault = object()
def getitem(obj, keyorindex, default=NoDefault):
    try:
        value = obj[keyorindex]
    except IndexError:
        if default is NoDefault:
            raise
        value = default
    return value

class FakeFrames(object):
    
    def fake_method(self):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_method")
        return currentframe()
    
    @property
    def fake_property(self):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_property")
        return currentframe()

    @classmethod
    def fake_classmethod(cls):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_classmethod")
        return currentframe()

    @staticmethod
    def fake_staticmethod():
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_method")
        return currentframe()

def fake_function():
    log = logging.getLogger("fakes")
    log.debug("in fake_function")
    return currentframe()

class BaseTest(unittest.TestCase):
    
    def assertModuleFileIs(self, first, second):
        name = os.path.basename(first)
        if name[-4:] in (".pyc", ".pyo"):
            name = name[:-4] + ".py"
        self.assertEquals(name, second,
            "%r != %r" % (name, second))

class TestUtils(BaseTest):
    
    def test_srcfile(self):
        self.assertModuleFileIs(srcfile("foo.py"), "foo.py")
        self.assertModuleFileIs(srcfile("foo.pyc"), "foo.py")
        self.assertModuleFileIs(srcfile("foo.pyo"), "foo.py")
        self.assertModuleFileIs(srcfile("foo"), "foo")

class TestFrameFuncs(BaseTest):
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
                self.assertModuleFileIs(result[k], v)
            else:
                self.assertEqual(v, result[k])

    def framefunc(self, framekey, expectedname):
        self.assertEquals(framefunc(self.frames[framekey]), expectedname)

    def test_callingframe_function(self):
        self.callingframe("function", 
            filename=os.path.basename(__file__),
            function="fake_function")

    def test_callingframe_method(self):
        self.callingframe("method",
            filename="tests.py",
            function="fake_method")

    def test_callingframe_property(self):
        self.callingframe("property",
            filename="tests.py",
            function="fake_property")

    def test_callingframe_classmethod(self):
        self.callingframe("classmethod",
            filename="tests.py",
            function="fake_classmethod")

    def test_callingframe_staticmethod(self):
        self.callingframe("staticmethod",
            filename="tests.py",
            function="fake_staticmethod")

    def test_framefunc_function(self):
        self.framefunc("function", "fake_function")

    def test_framefunc_method(self):
        self.framefunc("method", "FakeFrames.fake_method")

class TestStackLogger(BaseTest):
    
    def setUp(self):
        log = logging.getLogger("fakes")
        log.propagate = False
        logging.logMultiprocessing = False
        handler = logging.handlers.BufferingHandler(10)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        self.log = log
        self.handler = handler

    def tearDown(self):
        self.log.removeHandler(self.handler)
        self.handler.close()
        del(self.handler)

    def getrecord(self, index=0):
        return getitem(self.handler.buffer, index, None)
