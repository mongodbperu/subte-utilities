# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import subte


class SubteTest(unittest.TestCase):

    def test_version_string(self):
        subte.version_tuple = (0, 0, 0)
        self.assertEqual(subte.get_version_string(), '0.0.0')
        subte.version_tuple = (1, 0, 0)
        self.assertEqual(subte.get_version_string(), '1.0.0')
        subte.version_tuple = (5, 0, '+')
        self.assertEqual(subte.get_version_string(), '5.0+')
        subte.version_tuple = (0, 4, 'b')
        self.assertEqual(subte.get_version_string(), '0.4b')

    def test_class_aliases(self):
        generator_class = subte.Generator
