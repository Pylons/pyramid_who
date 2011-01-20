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
import unittest


class WhoV2AuthenticationPolicyTests(unittest.TestCase):

    _tempdir = None

    def setUp(self):
        from pyramid.config import Configurator
        self.config = Configurator(autocommit=True)
        self.config.begin()

    def tearDown(self):
        self.config.end()
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTargetClass(self):
        from pyramid_who.whov2 import WhoV2AuthenticationPolicy
        return WhoV2AuthenticationPolicy

    def _makeFile(self, filename, tempdir=None, text=None):
        import os
        if tempdir is None:
            import tempfile
            tempdir = self._tempdir = tempfile.mkdtemp()
        result = os.path.join(tempdir, filename)
        if text is not None:
            f = open(result, 'w')
            f.write(text)
            f.close()
        return result

    def _makeOne(self, config_file=None, identifier_id='test', callback=None):
        if config_file is None:
            config_file = self._makeFile('who.ini', text='')
        if callback is None:
            return self._getTargetClass()(config_file, identifier_id)
        return self._getTargetClass()(config_file, identifier_id, callback)

    def _makeRequest(self, **kw):
        from pyramid.testing import DummyRequest
        return DummyRequest(**kw)

    def test_class_conforms_to_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyClass
        from pyramid.interfaces import IAuthenticationPolicy
        verifyClass(IAuthenticationPolicy, self._getTargetClass())

    def test_instance_conforms_to_IAuthenticationPolicy(self):
        from zope.interface.verify import verifyObject
        from pyramid.interfaces import IAuthenticationPolicy
        verifyObject(IAuthenticationPolicy, self._makeOne())

    def test_ctor_invalid_config_file_name(self):
        self.assertRaises(Exception, self._makeOne, '/nonesuch')

    def test_ctor_invalid_config_file_content(self):
        filename = self._makeFile('not-ini.txt', text='this is not an INI file')
        self.assertRaises(Exception, self._makeOne, filename)

    def test_unauthenticated_userid_no_identity_in_environ(self):
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), None)

    def test_unauthenticated_userid_w_api_in_environ(self):
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                   'repoze.who.api': DummyAPI('phred'),
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.unauthenticated_userid(request), 'phred')

    def test_authenticated_userid_no_identity_in_environ(self):
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_w_api_in_environ(self):
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                   'repoze.who.api': DummyAPI('phred'),
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'phred')

    def test_authenticated_userid_wo_callback_w_identity_in_environ(self):
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.authenticated_userid(request), 'phred')

    def test_authenticated_userid_w_callback_veto_w_identity_in_environ(self):
        def _callback(identity, request):
            return None
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne(callback=_callback)
        self.assertEqual(policy.authenticated_userid(request), None)

    def test_authenticated_userid_w_callback_pass_w_identity_in_environ(self):
        def _callback(identity, request):
            return ['phlyntstones']
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne(callback=_callback)
        self.assertEqual(policy.authenticated_userid(request), 'phred')

    def test_effective_principals_no_identity_in_environ(self):
        from pyramid.security import Everyone
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_w_api_in_environ(self):
        from pyramid.security import Authenticated
        from pyramid.security import Everyone
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                   'repoze.who.api': DummyAPI('phred'),
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         ['phred', Authenticated, Everyone])

    def test_effective_principals_wo_callback_w_identity_in_environ(self):
        from pyramid.security import Authenticated
        from pyramid.security import Everyone
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.effective_principals(request),
                         ['phred', Authenticated, Everyone])

    def test_effective_principals_w_callback_veto_w_identity_in_environ(self):
        from pyramid.security import Everyone
        def _callback(identity, request):
            return None
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne(callback=_callback)
        self.assertEqual(policy.effective_principals(request), [Everyone])

    def test_effective_principals_w_callback_pass_w_identity_in_environ(self):
        from pyramid.security import Authenticated
        from pyramid.security import Everyone
        def _callback(identity, request):
            return ['phlyntstones']
        ENVIRON = {'repoze.who.identity': {'repoze.who.userid': 'phred'}}
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne(callback=_callback)
        self.assertEqual(policy.effective_principals(request),
                         ['phred', 'phlyntstones', Authenticated, Everyone])

    def test_remember_w_api_in_environ(self):
        HEADERS = [('Fruit', 'Basket')]
        api = DummyAPI(headers=HEADERS)
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                   'repoze.who.api': api,
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.remember(request, 'phred'), HEADERS)
        self.assertEqual(api._remembered, {'repoze.who.userid': 'phred',
                                           'identifier': 'test',
                                          })

    def test_forget_w_api_in_environ(self):
        HEADERS = [('Fruit', 'Basket')]
        api = DummyAPI(authenticated='phred', headers=HEADERS)
        ENVIRON = {'wsgi.version': '1.0',
                   'HTTP_USER_AGENT': 'testing',
                   'repoze.who.api': api,
                  }
        request = self._makeRequest(environ=ENVIRON)
        policy = self._makeOne()
        self.assertEqual(policy.forget(request), HEADERS)
        self.assertEqual(api._forgtten, {'repoze.who.userid': 'phred'})


class DummyAPI:

    def __init__(self, authenticated=None, headers=()):
        self._authenticated = authenticated
        self._headers = headers

    def authenticate(self):
        if self._authenticated is not None:
            return {'repoze.who.userid': self._authenticated}

    def remember(self, identity=None):
        self._remembered = identity
        return self._headers

    def forget(self, identity=None):
        self._forgtten = identity
        return self._headers
