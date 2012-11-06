"""
Module iterchoices is intended as a helper to prevent cyclic dependencies between db models
and to prevent database queries before database tables are created by syncdb.

This code should be left alone or can be combined with other module
which is not dependent on any database model nor already existing db connection
for facilitating the normal order of loading modules.
"""

import logging
import re
import pprint
import sys
import traceback

log = logging.getLogger('iterchoices')
repeated_error = False

def iterchoices(func):
    """Iterator for lazy evaluation of choices for database models.

    Examle Usage:
        class SomeNewModel(models.Model):
            abc = XyzChoiceCharField('SomeModelName',... choices=iterchoices(get_choices)))
    A function for evaluating items of choices (e.g. get_choices) is not evaluated when
    a model class (e.g. SomeNewModel) is inicialized.
    It is called by database model when it is first needed, only one time,
    not until all other models have been initialized.
    First possible call is usually for Django managent commands with the internal attribute "requires_model_validation = True",
    by e.g. dbsync, validate and typically commands changing structure of database.
    """
    for item in func():
        yield item


def iterchoices_db(func):
    """
    Iterator for lazy evaluation of choices for database models, modified 
    for functions which need database access to get results.

    It is similar to "iterchoices" with the following difference:
    When the db model is thoroughly validated by database management commands (e.g. dbsync),
    all calls to "func" are skipped here to prevent possible failing database queries
    before database tables are created in the same transaction,
    which can be easy caused by livesettings.
    (The state of database connection could be broken without this workaround for some db backends.)
    """
    # This test determines the conditions for which the call to enumerating
    # function "func" is to be skipped. 
    #
    # Typically it should be skipped for syncdb and all commands which can be
    # usually called before the first syncdb. It should be called for commands
    # like runserver, runcgi, shell.
    # For many other commands is good both, either call or skip.
    #
    # This function should be tested with Django 1.2 and 1.3
    # (Django 1.2 has worse support for error treatment inside transactions)
    # and for different db backends: postgres, sqlite3 and tests environment
    #
    # It would be better to find a solution inot here but by fix in Livesettings
    # (it looks not possible without a change in django.db)
    command = introspect_management_command()
    if command in ('syncdb', 'test', 'satchmo_store.shop.management.commands.satchmo_copy_static') \
                or command.startswith('south.'):
        log.info('Skipped model choices initialization function <%s> because'
                 ' of syncdb or other database management command' % str(func).split()[1])
    else:
        log.debug('Called model choices initialization function <%s>' % str(func).split()[1])
        for item in func():
            yield item

def introspect_management_command():
    """
    Introspection, what Django management command is actually running.

    Possible return values are:
    a) name of Django management internal command, e.g. 'runserver', 'runfcgi', 'syncdb'
    b) full name of external management command, e.g. 'south.management.commands.syncdb'
    c) string 'handler' in the case of running under handlers like uwsgi or mod_python.
    """
    # Output of this function should be tested and have been tested with respect 
    # to different commands and production server configurations including
    # all above-mentioned, with different installation methods
    # including compressed .egg,
    # on different platforms: Linux, Windows + Mingw, Windows + Cygwin
    # and also with clonesatchmo.
    global repeated_error
    try:
        raise ZeroDivisionError
    except ZeroDivisionError:
        f = sys.exc_info()[2].tb_frame.f_back
    nidentify = 0  # how much steps of identification have been done
    command = ''
    try:
        while f is not None:
            co = f.f_code
            filename = co.co_filename.replace('\\', '/')
            if filename.find('/core/') >= 0 and nidentify < 3:
                # django.core is usually in '/django/core/' but it can be e.g. in /Django-x.y.z/core/ for some installation
                if filename.find('/core/management/base.',) >= 0:
                    name = co.co_name
                    if name in (('validate', 'handle'), ('execute',), ('run_from_argv',))[nidentify]:
                        nidentify += 1
                        # analyze first argument of execute(self, *args, **options)
                        if name == 'execute' and co.co_argcount == 1 and (co.co_flags & 0xC == 0xC):
                            command = f.f_locals[co.co_varnames[0]].__module__.replace('django.core.management.commands.', '')
                elif filename.find('/core/management/commands/') >= 0:
                    command = re.sub('.*/core/management/commands/(.*)\..*', '\\1', filename)
                    nidentify = 3
                elif filename.find('/core/handlers/') >= 0:
                    command = 'handler'
                    nidentify = 3
            f = f.f_back
    except (AttributeError, IndexError, TypeError):
        pass
    # TODO: Remove the following line in January 2012 if nothing similar is reported
    log.debug('Management command: %s' % command)
    if (not re.match('[a-z_0-9.]+$', command) or nidentify < 3) and not repeated_error:
        log.error('Internal error in introspect_management_command. Report it to the author: hynekcer\n' +
                    pprint.pformat(traceback.extract_stack()))
        repeated_error = True
    return command
