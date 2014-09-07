# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import argparse

from subte.process import Process, ProcessMode


class ProcessTest(unittest.TestCase):

    def setUp(self):
        self.proc1 = Process([])

        class Process2(Process):
            pass
        self.proc2 = Process2([])

        class Process3(Process):

            NAME = 'my-proc'
        self.proc3 = Process3([])

    def test_parser_prog(self):
        self.assertEquals(self.proc1.parser.prog, 'Process')
        self.assertEquals(self.proc2.parser.prog, 'Process2')
        self.assertEquals(self.proc3.parser.prog, 'my-proc')

    def test_process_without_modes(self):
        self.assertEquals(self.proc1.MODES, [])
        self.assertEquals(self.proc2.MODES, [])
        self.assertEquals(self.proc3.MODES, [])

        self.assertEquals(self.proc1.current_mode, None)
        self.assertEquals(self.proc2.current_mode, None)
        self.assertEquals(self.proc3.current_mode, None)

    def test_modes(self):
        class Mode1(ProcessMode):

            def set_arguments(self, subparser):
                pass

        class Mode2(Mode1):
            pass

        class MyProcess(Process):

            MODES = [Mode1, Mode2]

        proc = MyProcess(['mode1'])
        self.assertTrue(Mode1 in proc.MODES)
        self.assertTrue(Mode2 in proc.MODES)
        self.assertTrue(isinstance(proc.current_mode, Mode1))

    def test_set_arguments(self):
        class MyProcess(Process):

            def set_arguments(self, parser):
                self.set_arguments_was_called = True

        proc = MyProcess()
        self.assertTrue(proc.set_arguments_was_called)

    def test_run(self):
        class ExecuteProcess(Process):

            def execute(self):
                self.execute_was_called = True

        class NoExecuteProcess(Process):
            pass

        proc = ExecuteProcess([])
        proc.run()
        self.assertTrue(proc.execute_was_called)

        proc = NoExecuteProcess([])
        self.assertRaises(NotImplementedError, proc.run)

    def test_prepare_and_finish(self):
        class MyProcess(Process):

            def prepare(self):
                self.prepare_was_called = True

            def execute(self):
                pass

            def finish(self):
                self.finish_was_called = True

        proc = MyProcess()
        proc.run()
        self.assertTrue(proc.prepare_was_called)
        self.assertTrue(proc.finish_was_called)


class ProcessModeTest(unittest.TestCase):

    def test_not_impl_set_arguments(self):
        parser = argparse.ArgumentParser()
        self.assertRaises(NotImplementedError, ProcessMode,
                          parser.add_subparsers())

        class Mode(ProcessMode):
            pass
        parser = argparse.ArgumentParser()
        self.assertRaises(NotImplementedError, Mode, parser.add_subparsers())

    def test_impl_set_arguments(self):
        class Mode(ProcessMode):

            def set_arguments(self, subparser):
                pass
        parser = argparse.ArgumentParser()
        assert Mode(parser.add_subparsers())
