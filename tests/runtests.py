# -*- coding: utf-8 -*-
import os
import sys

from unittest import defaultTestLoader, TextTestRunner, TestSuite

TESTS = ('subte_test', 'process_test', 'generator_test', )


def make_suite(prefix='', extra=(), force_all=False):
    tests = TESTS + extra
    test_names = list(prefix + x for x in tests)
    suite = TestSuite()
    suite.addTest(defaultTestLoader.loadTestsFromNames(test_names))
    return suite


def additional_tests():
    """
    This is called automatically by setup.py test
    """
    return make_suite('tests.')


def main():
    my_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(my_dir, '..')))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--with-pep8', action='store_true', dest='with_pep8',
                      default=True)
    parser.add_option('--with-pyflakes', action='store_true',
                      dest='with_pyflakes', default=True)
    parser.add_option('--force-all', action='store_true', dest='force_all',
                      default=False)
    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
                      default=0)
    parser.add_option('-q', '--quiet', action='count', dest='quietness',
                      default=0)
    options, extra_args = parser.parse_args()
    if options.with_pep8:
        try:
            import pep8
        except ImportError:
            sys.stderr.write('# Could not find pep8 library.\n')
            sys.exit(1)

        guide_main = pep8.StyleGuide(
            ignore=[],
            paths=['subte/'],
            exclude=[],
            max_line_length=80,
        )
        guide_tests = pep8.StyleGuide(
            ignore=['E221'],
            paths=['tests/'],
            max_line_length=80,
        )
        for guide in (guide_main, guide_tests):
            report = guide.check_files()
            if report.total_errors:
                sys.exit(1)

    if options.with_pyflakes:
        try:
            import pyflakes
            assert pyflakes  # silence pyflakes
        except ImportError:
            sys.stderr.write('# Could not find pyflakes library.\n')
            sys.exit(1)

        from pyflakes import api, reporter
        warnings = api.checkRecursive(['subte', 'tests'],
                                      reporter._makeDefaultReporter())
        if warnings > 0:
            sys.exit(1)

    suite = make_suite('', tuple(extra_args), options.force_all)

    runner = TextTestRunner(verbosity=options.verbosity - options.quietness + 1)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == '__main__':
    main()
