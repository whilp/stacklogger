import os
import unittest

from stacklogger import srcfile

class TestUtils(unittest.TestCase):
    
    def test_srcfile(self):
        result = os.path.join(os.getcwd(), "foo.py")
        self.assertEquals(srcfile("foo.py"), result)
        self.assertEquals(srcfile("foo.pyc"), result)
        self.assertEquals(srcfile("foo.pyo"), result)
        self.assertEquals(srcfile("foo"), result[:-3])
