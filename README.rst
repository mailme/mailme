===========================
MailMe - manage your mails.
===========================

.. image:: https://travis-ci.org/mailme/mailme.png?branch=master
    :target: https://travis-ci.org/mailme/mailme
    :alt: Travis build status

.. warning::

   MailMe is under heavy development. Please don't use it.


Installation
------------

.. note::

   MailMe is being developed and tested on ArchLinux, Ubuntu and MacOSX. I doubt it'll work on Windows yet.


.. code-block:: bash

    $ Create your virtualenv (recommended, use virtualenvwrapper)
    $ mkvirtualenv mailme

    $ # Clone repository
    $ git clone git@github.com:mailme/mailme.git

    $ # Activate Environment and install
    $ workon mailme
    $ make develop

    $ # run tests
    $ make test


Edit settings
-------------

Create a new file ``src/mailme/settings.py`` with the following content:

.. code-block:: python

    from mailme.conf.development import *

Edit and adapt this file to your specific environment.


Setup the database
------------------

.. note::

    Please note that MailMe was developed with PostgreSQL in mind. It uses
    PostgreSQL-specific features and thus doesn't support anything else.


Create an empty new PostgreSQL database (any other supported by Django works too).

.. code-block:: bash

    $ createdb mailme_dev

.. note::

    You might need to apply a postgresql user (``createdb -U youruser``) e.g ``postgres``
    for proper permissions.


.. code-block:: bash

    $ python manage.py migrate


Superuser
---------

.. code-block:: bash

    $ # Create a new super user
    $ python manage.py createsuperuser


Run the server, celery and other services
-----------------------------------------

Other services being used:

* Celery, is being used to run [regular] tasks, e.g for mail output.


To start all services:

.. code-block:: bash

   $ honcho start

.. note::

    You can find the SSL version on `port 8000 <http://localhost:8000/>`_

.. note::

    Our celery configuration requires redis to be installed and running.
    Please make sure it's up!


Run the test-suite
------------------

.. code-block:: bash

    $ make test

Resources
---------

* `Documentation <https://mailme.io/>`_
* `Bug Tracker <https://github.com/mailme/mailme/issues>`_
* `Code <https://github.com/mailme/mailme>`_
