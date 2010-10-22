import inspect
import logging
import os
import sys

from logn import Logn

class ContextLogger(logging.Logger):

    def callingframe(self, frame):
        """Return the first non-logging related frame from *frame*'s stack."""
        # Frames in these files are logging-related and should be skipped.
        logfiles = (logging._srcfile, __file__)
        print '\n'.join((str(x) for x in inspect.getouterframes(frame)))
        for frame in inspect.getouterframes(frame):
            filename = frame[1]
            if filename not in logfiles:
                return frame

    def framecontext(self, frame):
        rest = frame[1:]
        frame = frame[0]
        context = [frame.f_code.co_name]
		instance = frame.f_locals
		if "self
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

logging.setLoggerClass(ContextLogger)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(context)s:%(message)s",
)

logn = Logn(*[open(f) for f in sys.argv[1:]])
for fname, line in logn:
    print fname, line
