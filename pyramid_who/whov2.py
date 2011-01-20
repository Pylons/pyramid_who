##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################
import os

from zope.interface import implements

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated
from pyramid.security import Everyone
from repoze.who.config import make_api_factory_with_config as APIFactory


def _null_callback(identity, request):
    return ()

class WhoV2AuthenticationPolicy(object):
    implements(IAuthenticationPolicy)

    def __init__(self, config_file, identifier_id, callback=_null_callback):
        config_file = self._config_file = os.path.abspath(
                                          os.path.normpath(
                                          os.path.expandvars(
                                          os.path.expanduser(
                                            config_file))))
        conf_dir, _ = os.path.split(config_file)
        global_conf = {'here': conf_dir}
        self._api_factory = APIFactory(global_conf, config_file)
        self._identifier_id = identifier_id
        self._callback = callback

    def unauthenticated_userid(self, request):
        return self._get_identity(request)

    def authenticated_userid(self, request):
        """ See IAuthenticationPolicy.
        """
        identity = self._get_identity(request)

        if identity is not None:
            groups = self._callback(identity, request)
            if groups is not None:
                return identity['repoze.who.userid']

    def effective_principals(self, request):
        """ See IAuthenticationPolicy.
        """
        identity = self._get_identity(request)
        groups = self._get_groups(identity, request)
        if len(groups) > 1:
            groups.insert(0, identity['repoze.who.userid'])
        return groups

    def remember(self, request, principal, **kw):
        """ See IAuthenticationPolicy.
        """
        api = self._getAPI(request)
        identity = {'repoze.who.userid': principal,
                    'identifier': self._identifier_id,
                   }
        return api.remember(identity)

    def forget(self, request):
        """ See IAuthenticationPolicy.
        """
        api = self._getAPI(request)
        identity = self._get_identity(request)
        return api.forget(identity)

    def _getAPI(self, request):
        return self._api_factory(request.environ)

    def _get_identity(self, request):
        identity = request.environ.get('repoze.who.identity')
        if identity is None:
            api = self._getAPI(request)
            identity = api.authenticate()
        return identity

    def _get_groups(self, identity, request):
        if identity is not None:
            dynamic = self._callback(identity, request)
            if dynamic is not None:
                groups = list(dynamic)
                groups.append(Authenticated)
                groups.append(Everyone)
                return groups
        return [Everyone]
