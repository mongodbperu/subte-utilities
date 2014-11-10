# -*- coding: utf-8 -*-
import json
import logging
import os
import os.path
import re
import shutil

from unicodedata import normalize

try:
    from pymongo import MongoClient
except ImportError:  # pragma: no cover
    from pymongo import Connection as MongoClient  # pragma: no cover

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
    __FILENAME_FORMAT = '{number:02d}-{flat_concept}-{file_type}.{extension}'
    __FLAT_CONCEPT_REGEX = re.compile(r'[\t !"#$%&\'()*\:\;\-/<=>?@\[\\\]^_`{|'
                                       '},.]+')

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

    def handle(self):
        for index, item in enumerate(self.mapping):
            self.process_item(index + 1, item)

    def process_item(self, number, item):
        has_lecture = 'lecture' in item
        has_answer = 'answer' in item
        if not has_lecture and not has_answer:
            logging.warning('"{}" has not lecture and answer.'.format(
                item['concept']))
            return
        flat_concept = self.get_flat_concept(item['concept'])
        if has_lecture != has_answer:
            file_type = 'lecture' if has_lecture else 'answer'
            source = '{}.{}'.format(item[file_type],
                                    self.arguments.caption_extension)
            filename = self.get_filename(number, flat_concept, file_type)
            self.copy_file(source, filename)
        else:
            for file_type in ['lecture', 'answer']:
                if file_type in item:
                    source = '{}.{}'.format(item[file_type],
                                            self.arguments.caption_extension)
                    filename = self.get_filename(number, flat_concept,
                                                 file_type)
                    self.copy_file(source, filename)

    def get_flat_concept(self, concept):
        result = []
        for word in self.__FLAT_CONCEPT_REGEX.split(concept.lower()):
            if word:
                result.append(normalize('NFKD', word).encode('ascii',
                                                             'ignore'))
        return unicode('_'.join(result))

    def get_filename(self, number, flat_concept, file_type):
        return self.__FILENAME_FORMAT.format(**{
            'number': number,
            'flat_concept': flat_concept,
            'file_type': file_type,
            'extension': self.arguments.caption_extension
        })

    def copy_file(self, origin, destination):
        if self.arguments.reverse:
            destination, origin = origin, destination
        try:
            shutil.copy(os.path.join(self.arguments.source_dir, origin),
                        os.path.join(self.arguments.target_dir, destination))
            logging.info('Copied {} to {}'.format(origin, destination))
        except IOError as e:
            logging.error(e)


def main():
    generator = Generator()
    generator.run()

if __name__ == '__main__':
    main()
