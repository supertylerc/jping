"""Provides several utility classes for use by jping.
"""

from argparse import ArgumentParser
from argparse import ArgumentTypeError
import os
import sqlite3
import yaml


class Utils(object):
    """Provides static utility methods.
    """
    @staticmethod
    def parse_arguments():
        """Parse script arguments.

        :returns: A dict of the arguments passed.
        """

        parser = ArgumentParser(description="Ping all ARP entries.")
        parser.add_argument("-c", "--check", help="`pre` or `post`")
        parser.add_argument('-p', '--pre', action='store_true',
                            help='This script should be run before a maintenance.')
        parser.add_argument('-a', '--post', action='store_true',
                            help='This script should be run after a maintenance.')
        args = parser.parse_args()
        # These checks should be removed in v0.4.0 when `--check` is removed.
        if args.pre and args.post:
            raise ArgumentTypeError('You cannot specify both `--pre` and --`post`.')
        if args.pre and args.check or args.post and args.check:
            raise ArgumentTypeError('Do not use the old style `--check` with `--pre` or `--post`.')
        if not args.pre and not args.post and not args.check:
            raise ArgumentTypeError('You must specify either `--pre` or `--post`.')
        return args

    @staticmethod
    def parse_yaml(yaml_file):
        """Parse yaml files.

        :param yaml_file: path to a YAML file
        :type yaml_file: string or unicode
        :returns: dict of yaml data
        :rtype: dict
        """
        with open(yaml_file) as fname:
            return yaml.load(fname)


class DBase(object):
    """Database object for interacting with SQLite3.

    :attr: database: SQLite3 database path/name.
    :attr: _connection: The connection to the SQLite3 database.
    """
    def __init__(self, *args, **kwargs):
        """Creates a database connection.

        :param database: relative or aboslute path to a sqlite3 database
        """
        self.database = args[0] if len(args) else kwargs.get('database', 'jping.db')
        is_new = not os.path.exists(self.database)
        self._connection = sqlite3.connect(self.database)
        self._connection.row_factory = sqlite3.Row
        if is_new:
            self.create_schema()

    def create_schema(self):
        """Creates the table schema for jping.
        """
        schema = '''CREATE TABLE jping (
                     ip_address text not null,
                     interface text not null,
                     hostname text not null,
                     ping_results integer not null,
                     UNIQUE(ip_address, hostname)
                 )
                 '''
        self.query(schema)

    def query(self, query, params=list(), many=False):
        """Executes a single query against the database.

        :param query: SQL query to execute
        :type query: str or unicode
        :param params: bindings to pass to `cursor.execute`
        :type params: list
        :returns: `cursor`
        :rtype: cursor
        """
        with self._connection:
            cursor = self._connection.cursor()
            if many:
                return cursor.executemany(query, params)
            else:
                return cursor.execute(query, params)

    def close(self):
        """Closes the SQLite3 connection

        :returns: true or false
        """
        return self._connection.close()
