# -*- coding: utf-8 -*-
import logging
import sys
import time

try:
    import curses
except ImportError:
    curses = None


def _stderr_supports_color():
    color = False
    if curses and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                color = True
        except Exception:
            pass
    return color


class LogFormatter(logging.Formatter):

    def __init__(self, color=True, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)
        self._color = color and _stderr_supports_color()
        if self._color:
            fg_color = (curses.tigetstr("setaf") or
                        curses.tigetstr("setf") or "")
            if (3, 0) < sys.version_info < (3, 2, 3):
                fg_color = unicode(fg_color, "ascii")
            self._colors = {
                logging.DEBUG: unicode(curses.tparm(fg_color, 4), "ascii"),
                logging.INFO: unicode(curses.tparm(fg_color, 2), "ascii"),
                logging.WARNING: unicode(curses.tparm(fg_color, 3), "ascii"),
                logging.ERROR: unicode(curses.tparm(fg_color, 1), "ascii"),
            }
            self._normal = unicode(curses.tigetstr("sgr0"), "ascii")

    def format(self, record):
        try:
            record.message = record.getMessage()
        except Exception, e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)
        assert isinstance(record.message, basestring)
        record.asctime = time.strftime(
            "%Y-%m-%d %H:%M:%S", self.converter(record.created))
        prefix = ('[%(levelname)-8s %(asctime)s %(process)s %(module)s:'
                  '%(lineno)d]') % record.__dict__
        if self._color:
            prefix = (self._colors.get(record.levelno, self._normal) +
                      prefix + self._normal)
        try:
            message = unicode(record.message)
        except UnicodeDecodeError:
            message = repr(record.message)
        formatted = prefix + " " + message
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted = formatted.rstrip() + "\n" + record.exc_text
        return formatted.replace("\n", "\n    ")


def setup(level):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    channel = logging.StreamHandler()
    channel.setFormatter(LogFormatter())
    root_logger.addHandler(channel)
