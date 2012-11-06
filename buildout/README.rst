Installation
============

Rename "source" directory in "src"::
    mv source/ src

Create a file named ``buildout.cfg`` with the following content::

    [buildout]
    extends = conf/development.cfg

The ``extends`` line can have different values, and each value will result in a
different buildout profile being loaded.

The various profiles are:

conf/development.cfg
    Development buildout: barebone Django_ using SQLite_

conf/staging.cfg
    Staging and pre-production: uses PostgreSQL_, memcached_ and gunicorn_ for
    a production-ready configuration

Requirements
============

Here are listed the full requirements for the buildouts. *Common* holds the
requirement common to any buildout, while the section specific ones refer just
to the kind of buildout identified by the title.

Common
------

* Pyhton 2.7
* Mercurial
* Git
* gcc, g++
* zlib (with headers)
* openssl (with headers)
* libcrypto (with headers)
* libstdc++ (with headers)
* libjpeg (with headers)
* freetype (with headers)


Staging
-------

* libevent (with headers)
* readline (with headers)
* gettext (with headers)
* libxrender1 (OS 64 bit)
* libfontconfig1 (OS 64 bit)
* fontconfig-config (OS 64 bit)
* ttf-dejavu-core (OS 64 bit)

Bootstrapping
=============

Preparation
-----------

In case you are using a staging or production buildout, you must first start
supervisord_ with::

    $ bin/supervisordd -n

``-n`` has it run in foreground, so that you can stop it after bootstrapping
and have it launched more properly by some init script.

Creating the database
---------------------

First, run::

    $ bin/django syncdb

Answer ``yes`` when you will be requested to set up an administration user. Note
that ``syncdb`` should just create the tables for the applications not
supporting South_.

.. note::
   If you are in a production or staging environment, you should run ``syncdb``
   only when you set the buildout up for the first time: everything else should
   be managed via South_.

Next, you need to bring up-to-date (which means creating the tables, but only
in the bootstrapping context) all the other tables::

    $ bin/django migrate product.modules.configurable
    $ bin/django migrate product
    $ bin/django migrate satchmo_store.contact
    $ bin/django migrate satchmo_store.shop
    $ bin/django migrate satchmoutils
    $ bin/django migrate satchmoutils.tax.modules.noarea
    $ bin/django migrate primifrutti.shop
    $ bin/django migrate primifrutti.zones
    $ bin/django migrate primifrutti.invites



Populating the database
-----------------------

Finally, you need to load all the data needed to bootstrap the system::

    $ bin/django loaddata initial_setup.yaml

To import the demo images, read ``fixtures/README.txt``.

Updating
========

When you have to update an existing installation, after running the usual steps
(such as ``bin/develop up``) you must also:

    1. Stop Django_ via ``bin/supervisordctl stop django``
    2. Migrate the database
    3. Restart Django_ via ``bin/supervisordctl start django``

The second step is done by invoking::

    $ bin/django migrate

Refer to the `South documentation`_ for more information about the command.

Development info
================

Starting the server
-------------------

To start the system run::

    $ bin/django runserver

And then point your browser to http://localhost:8000.

Models changes
--------------

.. note::
   You should definitely read the `South documentation`_ before developing.

If you have done **any modification** to a ``models.py`` file, or at any rate
you have made a modification that requires a change on the database, you
**must** include in the commit that contains the modification all the necessary
South_ migrations (schema migrations and data migrations if necessary).

This means that any commit that somehow alter how the model is represented onto
the database will be rollbacked if the commit diff involves only ``models.py``
and doesn't include one or more related migrations in ``migrations/``.

If you have made a simple change, try running the following command::

    $ bin/django schemamigration <app_name> --auto

Where ``app_name`` is the name of the application where the ``models.py`` file
that you have modified resides. The output will tell you what files have been
created: **please review them**.

If the changes you have made also require a data migration (for example you
might have split ``full_name`` into ``first_name`` and ``last_name``) you must
also create a so called *data migration*.

*Data migrations* can't be automatized, and they have to be edited
manually. First, run::

    $ bin/django datamigration <app_name> <migration_name>

Where ``migration_name`` is the explaining name of our migration. Keeping up
with the example, it could be ``fullname_split``.

Once this command has run, you should open and edit the generated file as
explained in `data migrations`_.

.. _Django: http://www.djangoproject.com
.. _SQLite: http://www.sqlite.org/
.. _PostgreSQL: http://www.postgresql.org/
.. _South: http://south.aeracode.org
.. _supervisord: http://supervisord.org/
.. _`South documentation`: http://south.aeracode.org/docs/index.html
.. _`data migrations`: http://south.aeracode.org/docs/tutorial/part3.html#data-migrations
