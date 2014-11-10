# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest

import argparse

from subte.process import Process, ProcessMode

from tests.utils import capture_sys_output


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
        self.initialize_mode2_was_called = False
        self.initialize_mode3_was_called = False

        class Mode1(ProcessMode):

            def set_arguments(self, subparser):
                pass

        class Mode2(Mode1):

            def initialize(mode_self, arguments):
                attr_format = 'initialize_{}_was_called'
                name = attr_format.format(mode_self.__class__.__name__.lower())
                setattr(self, name, True)

        class Mode3(Mode2):
            pass

        class MyProcess(Process):

            MODES = [Mode1, Mode2, Mode3]

        with self.assertRaises(SystemExit):
            with capture_sys_output() as (stdout, stderr):
                MyProcess([])
        self.assertIn('too few arguments', stderr.getvalue())

        with self.assertRaises(SystemExit):
            with capture_sys_output() as (stdout, stderr):
                MyProcess(['unknown'])
        self.assertIn("invalid choice: 'unknown'", stderr.getvalue())

        proc = MyProcess(['mode1'])
        for mode in [Mode1, Mode2, Mode3]:
            self.assertIn(mode, proc.MODES)

        self.assertTrue(isinstance(proc.current_mode, Mode1))
        self.assertFalse(self.initialize_mode2_was_called)
        self.assertFalse(self.initialize_mode3_was_called)

        self.initialize_mode2_was_called = False
        self.initialize_mode3_was_called = False
        proc = MyProcess(['mode2'])
        self.assertTrue(isinstance(proc.current_mode, Mode2))
        self.assertTrue(self.initialize_mode2_was_called)
        self.assertFalse(self.initialize_mode3_was_called)

        self.initialize_mode2_was_called = False
        self.initialize_mode3_was_called = False
        proc = MyProcess(['mode3'])
        self.assertTrue(isinstance(proc.current_mode, Mode3))
        self.assertFalse(self.initialize_mode2_was_called)
        self.assertTrue(self.initialize_mode3_was_called)

    def test_set_arguments(self):
        class MyProcess(Process):

            def set_arguments(self, parser):
                self.parser.add_argument('-a', default=True)
                self.parser.add_argument('-b', default=False)

        proc = MyProcess([])
        self.assertTrue(proc.arguments.a)
        self.assertFalse(proc.arguments.b)

    def test_handle(self):
        self.handle_was_called = False

        class ExecuteProcess(Process):

            def handle(process_self):
                self.handle_was_called = True

        class NoExecuteProcess(Process):
            pass

        proc = ExecuteProcess([])
        proc.run()
        self.assertTrue(self.handle_was_called)

        proc = NoExecuteProcess([])
        proc.run()

    def test_prepare_and_finish(self):
        self.prepare_was_called = False
        self.finish_was_called = False

        class MyProcess(Process):

            def prepare(process_self):
                self.prepare_was_called = True

            def handle(self):
                pass

            def finish(process_self):
                self.finish_was_called = True

        proc = MyProcess([])
        proc.run()
        self.assertTrue(self.prepare_was_called)
        self.assertTrue(self.finish_was_called)

    def test_handle_exception(self):
        self.handle_exception_was_called = False

        class MyProcess(Process):

            def handle(process_self):
                raise Exception

            def handle_exception(process_self, e):
                self.handle_exception_was_called = True

        proc = MyProcess([])
        proc.run()
        self.assertTrue(self.handle_exception_was_called)


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

    def test_initialize(self):
        self.initialize_was_called = False

        class Mode(ProcessMode):

            def set_arguments(self, subparser):
                pass

            def initialize(mode_self, arguments):
                self.initialize_was_called = True

        parser = argparse.ArgumentParser()
        mode = Mode(parser.add_subparsers())
        self.assertFalse(self.initialize_was_called)
        mode.initialize(None)
        self.assertTrue(self.initialize_was_called)
