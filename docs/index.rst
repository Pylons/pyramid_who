:mod:`pyramid_who`
==================

:mod:`pyramid_who` is an extension for the :mod:`pyramid` web framework,
providing an authentication policy based on the "new" :mod:`repoze.who` API,
as found in version 2.0 and greater.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

  $ easy_install pyramid_who

Usage
-----

Configure the :class:`WhoV2AuthenticationPolicy` into your :mod:`pyramid`
application via imperative Python code:

.. code-block:: python
   import os

   from pyramid.authorization import ACLAuthorizationPolicy
   from pyramid.config import Configurator
   from pyramid_who.whov2 import WhoV2AuthenticationPolicy
   from my_package.users import verify_user

   config_file = '/path/towho.ini'
   identifier_id = 'auth_tkt'
   authentication_policy = WhoV2AuthenticationPolicy(config_file,
                                                     identifier_id,
                                                     callback=verify_user)
   authorization_policy = ACLAuthorizationPolicy()
   config = Configurator(authentication_policy=authentication_policy,
                         authorization_policy=authorization_policy)

or via ZCML:

.. code-block:: xml
   :linenos:

   <include
    package="pyramid_who"
    file="meta.zcml"
    />

   <whov2authenticatonpolicy
    config_file="/path/to/who.ini"
    identifier_id="auth_tkt"
    callback="my_package.users.verify_user"
    />


``config_file``
    A fully-qualified path to a :mod:`repoze.who` configuration file.

``identifier_id``
    The ID within that file of the :mod:`repoze.who` authentication plugin
    used to "remember" and "forget" authenticated users.

``callback``
    A function taking ``identity`` (a :mod:`repoze.who` identity mapping)
    and ``request``, and returning a sequence of group IDs for the user, if
    she exists.  If not, the callback must return None.


Interaction with :mod:`repoze.who` Middleware
---------------------------------------------

If your application is deployed with the middleware from :mod:`repoze.who`
active, the plugin will use the identity and API objects which the middleware
injects into the WSGI environment.  Otherwise, it will use the supplied
configuration file to create a :mod:`repoze.who` API instance when needed.


Reporting Bugs / Development Versions
-------------------------------------

Visit https://github.com/Pylons/pyramid_who/issues to report bugs.
Visit https://github.com/Pylons/pyramid_who to download development or
tagged versions.

Indices and tables
------------------

* :ref:`modindex`
* :ref:`search`
