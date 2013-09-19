from __future__ import absolute_imports

import sys

import sqlalchemy

from declarative import ModelFactory
from sqlautocode import config
from sqlautocode import constants
from sqlautocode import formatter
from sqlautocode import util


def generate_tables(options, db, tablenames, reflection_schema):
    """
    Generate all code for tablenames that we desire to create
    """
    metadata = sqlalchemy.MetaData(db)
    for tname in tablenames:
        print >>config.err, "Generating python model for table %s" % (
            util.as_sys_str(tname))

        table = sqlalchemy.Table(tname, metadata, schema=reflection_schema,
                                 autoload=True)
        if options.schema is None:
            # we're going to remove the schema from the table so that it
            #  isn't rendered in the output.  If we don't put back the
            #  correct value, it may cause errors when other tables reference
            #  this one.
            original_schema = table.schema
            table.schema = None
        else:
            original_schema = options.schema

        INC = '\n\n'
        if options.z3c:
            INC = INC + 4*' '

        util.emit('%s%s%s%s = %r' % (
            INC, options.table_prefix, tname, options.table_suffix, table)
        )

        if options.z3c:
            util.emit(INC + ('class %(tn)sObject(MappedClassBase): pass\n'
                             'mapper(%(tn)sObject, %(tn)s)') % {'tn': tname})

        table.schema = original_schema

        # directly print indices after table def
        if not options.noindex:
            indexes = []
            if not table.indexes:
                # for certain dialects we need to include index support
                if hasattr(db.dialect, 'indexloader'):
                    indexes = db.dialect.indexloader(db).indexes(table)
                else:
                    print >> config.err, (
                        'It seems that this dialect does not support indexes!'
                    )
            else:
                indexes = list(table.indexes)

            util.emit(*[repr(index) for index in indexes])


def get_dialect(options, db):
    """
    Get the engine dialect
    """
    # some header with imports
    return (
        "" if not options.generictypes else
        "from sqlalchemy.databases.%s import *\n" % db.name
    )


def get_reflection_schema(options, db, connection):
    """
    Get the reflection schema
    """
    if options.schema is None:
        try:
            return db.dialect._get_default_schema_name(connection)
        except NotImplementedError:
            return


def get_specified_tablenames(options, tablenames):
    """
    If the user specified tablenames to generate then search for them, and
    validate input
    """
    subset, missing, unglobbed = util.glob_intersection(tablenames,
                                                        options.tables)
    if not subset:
        for identifier in missing:
            print >>config.err, 'Table "%s" not found.' % identifier
        for glob in unglobbed:
            print >>config.err, '"%s" matched no tables.' % glob
        print >>config.err, "No tables matched!"
        sys.exit(1)
    else:
        return subset


def run_declarative_factory(options):
    """
    Run the declarative factory
    """
    config.interactive = None if not options.interactive else True
    config.schema = options.schema or None
    config.example = False if not options.example else True
    factory = ModelFactory(config)
    util.emit(repr(factory))
    config.out.close()
    config.out = sys.stdout
    print >>config.err, "Output written to %s" % options.output


def main():
    """
    Console Script Entry Point
    """
    config.configure()
    options = config.options
    if options.declarative:
        run_declarative_factory(options)
        return

    formatter.monkey_patch_sa()
    db, options = config.engine, config.options
    print >>config.err, 'Starting...'
    connection = db.connect()
    reflection_schema = options.schema or get_reflection_schema(
        options, db, connection
    )
    tablenames = db.dialect.get_table_names(connection, reflection_schema)
    if options.tables:
        tablenames = get_specified_tablenames(options, tablenames)

    dialect = get_dialect(options, db)

    header = options.z3c and constants.HEADER_Z3C or constants.HEADER
    util.emit(header % {'dialect': dialect, 'encoding': options.encoding})

    if options.z3c:
        util.emit(constants.FOOTER_Z3C)

    # print some example
    if options.example:
        util.emit('\n' + constants.FOOTER_EXAMPLE % {
            'url': unicode(db.url), 'tablename': tablenames[0]})

    if options.output:
        util.emit('\n')
        config.out.close()
        config.out = sys.stdout
        print >>config.err, "Output written to %s" % options.output
