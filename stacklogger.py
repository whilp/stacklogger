import inspect
import logging
import os
import sys
import types

__all__ = ["srcfile", "callingframe", "framefunc", "StackLogger"]
__todo__ = [item for item in """
 * make method/function args/values available in log format
""".split(" * ") if item]

NoMatch = object()

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

    *frame* should be a Python interpreter stack frame with a current
    code object (or a sequence with such a frame as its first element).
    :meth:`framefunc` will try to determine where the calling function was
    defined; if the function was defined in a class (as with properties,
    methods and classmethods), the class' name will be prepended to the function
    name (like *class.function*).
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
    instance = None
    try:
        instance = frame.f_locals[frame.f_code.co_varnames[0]]
        cls = instance.__class__
        obj = cls.__dict__[name]
        log.debug("Found %s attribute on instance %s", name, instance)
    except accesserr:
        obj = getattr(instance, name, NoMatch)
        if obj is not NoMatch:
            cls = instance

    if obj is not NoMatch:
        context.insert(0, cls.__name__)
    return '.'.join(context)

class StackLogger(logging.Logger):
    """A logging channel.

    A :class:`StackLogger` inspects the calling context of a
    :class:`logging.LogRecord`, adding useful information like the class where
    a method was defined to the standard :class:`logging.Formatter` 'funcName'
    attribute.
    """

    def findCaller(self):
        """Return the filename, line number and function name of the caller's frame."""
        frame = inspect.currentframe()
        filename = "(unknown file)"
        lineno = 0
        funcName = "(unknown function)"
        try:
            frame = callingframe(frame)
            funcName = framefunc(frame)
            filename, lineno = frame[1:3]
        finally:
            # Make sure we don't leak a reference to the frame to prevent a
            # reference cycle.
            del(frame)

        return (os.path.normcase(filename), lineno, funcName)
