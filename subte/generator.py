# -*- coding: utf-8 -*-
import json
import logging
import os
import os.path
import re
import shutil
import sys

from datetime import datetime
from unicodedata import normalize

try:
    from pymongo import MongoClient
except ImportError:
    from pymongo import Connection
    MongoClient = Connection
from pymongo.errors import ConnectionFailure

from subte.process import Process, ProcessMode


class JSONMode(ProcessMode):

    SUBCOMMAND = 'json'
    HELPTEXT = 'Extract captions mapping from a JSON file'
    DESCRIPTION = 'JSON mode'

    def set_arguments(self, subparser):
        subparser.add_argument('file', type=str, help='Mapping file')

    def initialize(self, arguments):
        with open(arguments.file) as fd:
            self.mapping = json.loads(fd.read())


class MongoDBMode(ProcessMode):

    SUBCOMMAND = 'db'
    HELPTEXT = 'Extract captions mapping from a MongoDB database'
    DESCRIPTION = 'MongoDB database mode'

    def set_arguments(self, subparser):
        subparser.add_argument('uri', type=str, help='MongoDB URI')
        subparser.add_argument('collection', type=str,
                               help='MongoDB collection')

    def initialize(self, arguments):
        connection = MongoClient(arguments.uri)
        db = connection.get_default_database()
        self.mapping = list(db[arguments.collection].find())
        connection.disconnect()


class Generator(Process):

    NAME = 'subte-gen'
    MODES = [JSONMode, MongoDBMode]

    __MAPPING_FORMAT = {
        'lecture': '{number:02d}a-{flat_concept}-Lecture.{extension}',
        'answer': '{number:02d}b-{flat_concept}-Answer.{extension}'
    }
    __MAPPING_FORMAT2 = {
        True: '{number:02d}-{flat_concept}-Lecture.{extension}',
        False: '{number:02d}-{flat_concept}-Answer.{extension}'
    }
    __RE_FLAT_CONCEPT = re.compile(r'[\t !"#%&\'*\:\;\-/<=>?@\[\\\]^_`{|},.]+')

    def set_arguments(self, parser):
        parser.add_argument('-s', '--source_dir', type=str, required=True,
                            help='Source captions directory')
        parser.add_argument('-t', '--target_dir', type=str, required=True,
                            help='Destination captions directory')
        parser.add_argument('-c', '--caption_extension', type=str,
                            default='srt', help='Captions extension')
        parser.add_argument('-r', '--reverse', dest='reverse',
                            action='store_true', default=False,
                            help='Perform the reverse process')
        parser.add_argument('-f', '--force', dest='force', action='store_true',
                            default=False,
                            help='Force creation of destination directory')

    def prepare(self):
        if not hasattr(self.current_mode, 'mapping'):
            raise ValueError('current_mode must have a mapping attribute.')
        self.mapping = self.current_mode.mapping
        if (self.arguments.force and
           not os.path.exists(self.arguments.target_dir)):
            os.makedirs(self.arguments.target_dir)

    def execute(self):
        i = 0
        for item in self.mapping:
            result = self.process_item(i + 1, item)
            i += int(result)

    def process_item(self, number, item):
        has_lecture = 'lecture' in item
        has_answer = 'answer' in item
        if not has_lecture and not has_answer:
            logging.warning('"{}" has not lecture and answer.'.format(
                item['concept']))
            return False
        flat_concept = self.get_flat_concept(item['concept'])
        if has_lecture != has_answer:
            source = '{}.{}'.format(item[{True: 'lecture',
                                          False: 'answer'}[has_lecture]],
                                    self.arguments.caption_extension)
            filename = self.get_filename(self.__MAPPING_FORMAT2[has_lecture],
                                         number, flat_concept)
            result = self.copy_file(source, filename)
        else:
            if has_lecture:
                source = '{}.{}'.format(item['lecture'],
                                        self.arguments.caption_extension)
                filename = self.get_filename(self.__MAPPING_FORMAT['lecture'],
                                             number, flat_concept)
                result = self.copy_file(source, filename)
            if has_answer:
                source = '{}.{}'.format(item['answer'],
                                        self.arguments.caption_extension)
                filename = self.get_filename(self.__MAPPING_FORMAT['answer'],
                                             number, flat_concept)
                result = self.copy_file(source, filename)
        return result

    def get_flat_concept(self, concept):
        concept = concept.replace('(', '')
        concept = concept.replace(')', '')
        result = []
        for word in self.__RE_FLAT_CONCEPT.split(concept):
            result.append(normalize('NFKD', word).encode('ascii', 'ignore'))
        return unicode('_'.join(result))

    def get_filename(self, filename_format, number, flat_concept):
        return filename_format.format(**{
            'number': number,
            'flat_concept': flat_concept,
            'extension': self.arguments.caption_extension
        })

    def copy_file(self, origin, destination):
        if self.arguments.reverse:
            destination, origin = origin, destination
        try:
            shutil.copy(os.path.join(self.arguments.source_dir, origin),
                        os.path.join(self.arguments.target_dir, destination))
        except Exception as e:
            logging.error(e, exc_info=True)
            return True
        logging.info('Copied {} to {}'.format(origin, destination))
        return True


def main():
    generator = Generator()
    generator.run()

if __name__ == '__main__':
    main()
