import inspect
import logging
import timeit

logging.logMultiprocessing = False

currentframe = inspect.currentframe

class FakeFrames(object):
    
    def fake_method(self):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_method")
    
    @property
    def fake_property(self):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_property")

    @classmethod
    def fake_classmethod(cls):
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_classmethod")

    @staticmethod
    def fake_staticmethod():
        log = logging.getLogger("fakes")
        log.debug("in FakeFrames.fake_staticmethod")

def fake_function():
    log = logging.getLogger("fakes")
    log.debug("in fake_function")

fake_lambda = lambda: logging.getLogger("fakes").debug("in fake_lambda")

contexts = {
    "function": fake_function,
    "lambda": fake_lambda,
    "class_classmethod": FakeFrames.fake_classmethod,
    "class_staticmethod": FakeFrames.fake_staticmethod,
}

fakes = FakeFrames()
for k in dir(fakes):
    if not k.startswith("fake_"):
        continue
    v = getattr(fakes, k)
    if k in ("fake_property",):
        v = lambda: getattr(fakes, "fake_property")
    contexts[k.replace("fake_", "", 1)] = v

def setup(cls):
    def dosetup():
        import logging
        logging.setLoggerClass(cls)

    return dosetup

import stacklogger
loggers = (logging.Logger, stacklogger.StackLogger)

num = int(1e5)
for k, v in contexts.items():
    stack = timeit.Timer(stmt=v, setup=setup(stacklogger.StackLogger)).timeit(num)
    regular = timeit.Timer(stmt=v, setup=setup(logging.Logger)).timeit(num)
    print "stack/regular %20s: %.02f%%" % (k, (100.0 * stack)/regular)
