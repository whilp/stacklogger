import inspect
import logging
import os
import sys

def srcfile(fname):
    srcfile = fname
    if hasattr(sys, 'frozen'): #support for py2exe
        srcfile = fname
    elif fname.lower()[-4:] in ['.pyc', '.pyo']:
        srcfile = fname[:-4] + '.py'
    return os.path.normcase(srcfile)

class StackLogger(logging.Logger):

    def callingframe(self, frame):
        """Return the first non-logging related frame from *frame*'s stack."""
        # Frames in these files are logging-related and should be skipped.
        logfiles = (logging._srcfile, __file__)
        for frame in inspect.getouterframes(frame):
            filename = frame[1]
            if filename not in logfiles:
                return frame

    def framecontext(self, frame):
        rest = frame[1:]
        frame = frame[0]
        context = [frame.f_code.co_name]

        # If the first argument to the frame's code is an instance, and that
        # instance has a method with the same name as the frame's code, assume
        # that the code is a method of that instance.
        try:
            instance = frame.f_locals[frame.f_code.co_varnames[0]]
            ismethod = instance.im_func.func_code == frame.f_code
        except (AttributeError, IndexError, KeyError):
            instance = None
            ismethod = False

        if ismethod:
            instance.insert(0, instance.__class__.__name__)
        return '.'.join(context)

    def makeRecord(self, name, level, fn, lno, msg, 
            args, exc_info, func=None, extra=None):
        rv = logging.Logger.makeRecord(self, name, level, fn, lno, msg, args,
            exc_info, func, extra)
        frame = inspect.currentframe()
        try:
            frame = self.callingframe(frame)
            rv.context = self.framecontext(frame)
        finally:
            # Make sure we don't leak a reference to the frame to prevent a
            # reference cycle.
            del(frame)

        return rv
