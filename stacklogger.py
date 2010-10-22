"""\
stacklogger provides a stack-aware extension of the standard library's logging
facility. With stacklogger, you can add useful information to your log messages
without changing any code or adding extra dependencies for your users to
install.
"""

import inspect
import logging
import os
import sys
import types

__all__ = ["srcfile", "callingframe", "framefunc", "StackLogger"]
__todo__ = [item for item in """
 * make method/function args/values available in log format
""".split(" * ") if item]

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# A logger for a logger...
logging.getLogger("stacklogger").addHandler(NullHandler())

def srcfile(fname):
    """Sanitize a Python module's filename.

    This function produces filenames similar to :data:`logging._srcfile` and
    those returned by :func:`inspect.getsourcefile`.
    """
    if fname.lower()[-4:] in (".pyc", ".pyo"):
        fname = fname.lower()[:-4] + ".py"
    return os.path.normcase(os.path.abspath(fname))

def callingframe(frame):
    """Return info about the first non-logging related frame from *frame*'s stack."""
    # Frames in these files are logging-related and should be skipped.
    logfiles = (logging._srcfile, srcfile(__file__))
    for frame in inspect.getouterframes(frame):
        filename = frame[1]
        if filename not in logfiles:
            return frame

def framefunc(frame):
    """Return a string representation of the code object at *frame*.

    *frame* should be a Python interpreter stack frame with a current code
    object (or a sequence with such a frame as its first element). If the code
    object is a method, :meth:`framefunc` will try to determine the class in
    which the method was defined.
    """
    log = logging.getLogger("stacklogger")
    if not isinstance(frame, types.FrameType):
        frame = frame[0]
    name = frame.f_code.co_name
    if name == "<module>":
        name = "__main__"
    log.debug("Building context for %s", name)
    context = [name]

    accesserr = (AttributeError, IndexError, KeyError)
    # If the first argument to the frame's code is an instance, and that
    # instance has a attribute with the same name as the frame's code, assume that
    # the code is a attribute of that instance. Use instance.__class__.__dict__
    # here because instance.name (or getattr(instance, name) can cause things
    # like properties to load in an infinite recursion.
    try:
        instance = frame.f_locals[frame.f_code.co_varnames[0]]
        cls = instance.__class__
        obj = cls.__dict__[name]
        log.debug("Found %s attribute on instance %s", name, instance)
        match = True
    except accesserr:
        match = False

    if match:
        context.insert(0, cls.__name__)
    return '.'.join(context)

class StackLogger(logging.Logger):
    """A logging channel.

    A StackLogger inspects the calling context of a :class:`logging.LogRecord`,
    adding useful information like the class where a method was defined to the
    standard :class:`logging.Formatter` 'funcName' attribute.
    """

    def makeRecord(self, name, level, fn, lno, msg, 
            args, exc_info, func=None, extra=None):
        """Build and return a :class:`logging.LogRecord`.

        This method inspects the calling stack to add more information to the
        usual :attr:`logging.LogRecord.funcName` attribute.
        """
        rv = logging.Logger.makeRecord(self, name, level, fn, lno, msg, args,
            exc_info, func, extra)
        funcName = rv.funcName
        frame = inspect.currentframe()
        try:
            frame = callingframe(frame)
            funcName = framefunc(frame)
        finally:
            # Make sure we don't leak a reference to the frame to prevent a
            # reference cycle.
            del(frame)

        rv.funcName = funcName
        return rv
