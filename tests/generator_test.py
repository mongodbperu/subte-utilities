# -*- coding: utf-8 -*-
import json
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from subte.process import Process
from subte.generator import JSONMode

from tests.utils import capture_sys_output


class JSONModeTest(unittest.TestCase):

    def setUp(self):
        class MyJSONProcess(Process):

            MODES = [JSONMode]

        self.proc_class = MyJSONProcess

    def test_process(self):
        with self.assertRaises(SystemExit):
            with capture_sys_output() as (stdout, stderr):
                self.proc_class([])
        self.assertIn('too few arguments', stderr.getvalue())

        with self.assertRaises(SystemExit):
            with capture_sys_output() as (stdout, stderr):
                self.proc_class(['unknown'])
        self.assertIn("invalid choice: 'unknown'", stderr.getvalue())

        with self.assertRaises(SystemExit):
            with capture_sys_output() as (stdout, stderr):
                self.proc_class(['json'])
        self.assertIn('too few arguments', stderr.getvalue())

        file_path = 'tests/unknown_mapping.json'
        with self.assertRaises(IOError) as cm:
            self.proc_class(['json', file_path])
            self.assertIn("No such file or directory: '{}'".format(file_path),
                          cm.exception.message)

        file_path = 'tests/mapping.json'
        proc = self.proc_class(['json', file_path])
        with open(file_path) as fd:
            self.assertEquals(proc.current_mode.mapping,
                              json.loads(fd.read()))
