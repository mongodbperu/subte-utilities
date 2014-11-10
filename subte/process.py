# -*- coding: utf-8 -*-
import argparse
import logging
import sys

from subte import log

LOGGING_LEVELS = [
    'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'
]


class ProcessMode(object):

    SUBCOMMAND = None
    HELPTEXT = None
    DESCRIPTION = None

    def __init__(self, subparsers):
        self.subparsers = subparsers
        self._set_subparser(subparsers)

    def _set_subparser(self, subparsers):
        subcmd = self.SUBCOMMAND or self.__class__.__name__.lower()
        subparser = self.subparsers.add_parser(subcmd, help=self.HELPTEXT,
                                               description=self.DESCRIPTION)
        self.set_arguments(subparser)
        self.subparser = subparser

    def set_arguments(self, subparser):
        """Useful to set mode-specific arguments.
        """
        raise NotImplementedError

    def initialize(self, arguments):
        """Useful to check the mode and process arguments values after parse
        them.
        """
        pass


class Process(object):

    NAME = None
    MODES = []

    @property
    def current_mode(self):
        """Returns the current mode instance for the process.
        """
        if not self.MODES:
            return None
        return self.__modes[self.arguments.subparser_name]

    def __init__(self, args=None):
        name = self.NAME or self.__class__.__name__
        self.parser = argparse.ArgumentParser(name)
        self.parser.add_argument('-l', '--logging', type=str, default='INFO',
                                 choices=LOGGING_LEVELS, help='Logging level')
        self.set_arguments(self.parser)
        if self.MODES:
            subparsers = self.parser.add_subparsers(title='Modes',
                                                    description='valid modes',
                                                    dest='subparser_name')
            self.__modes = {}
            for mode_class in self.MODES:
                mode_instance = mode_class(subparsers)
                subcmd = (mode_instance.SUBCOMMAND or
                          mode_instance.__class__.__name__.lower())
                self.__modes[subcmd] = mode_instance

        self.arguments = self.parser.parse_args(args)
        log.setup(self.arguments.logging)
        if self.current_mode:
            self.current_mode.initialize(self.arguments)

    def set_arguments(self, parser):
        """Useful to set process-specific arguments.
        """
        pass

    def prepare(self):
        pass

    def handle(self):
        raise NotImplementedError

    def finish(self):
        pass

    def log_exception(self, typ, value, tb):
        logging.error('Uncaught exception', exc_info=(typ, value, tb))

    def handle_exception(self, e):
        pass

    def run(self):
        try:
            self.prepare()
            self.handle()
            self.finish()
        except Exception as e:
            self.handle_exception(e)
            self.log_exception(*sys.exc_info())
            raise
