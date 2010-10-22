import unittest

from stacklogger import srcfile

class TestUtils(unittest.TestCase):
    
    def test_srcfile(self):
        self.assertTrue(srcfile("foo.py").endswith("foo.py"))
        self.assertTrue(srcfile("foo.pyc").endswith("foo.py"))
        self.assertTrue(srcfile("foo.pyo").endswith("foo.py"))
        self.assertTrue(srcfile("foo").endswith("foo"))
