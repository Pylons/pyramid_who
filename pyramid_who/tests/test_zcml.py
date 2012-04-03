import unittest


class TestRepozeWhoAuthenticationPolicyDirective(unittest.TestCase):

    _tempdir = None

    def setUp(self):
        from pyramid.testing import setUp
        self.config = setUp(autocommit=False)

    def tearDown(self):
        from pyramid.testing import tearDown
        tearDown()
        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _makeWhoConfig(self, name='who.ini'):
        import os
        import tempfile
        tempdir = self._tempdir = tempfile.mkdtemp()
        config_file = os.path.join(tempdir, 'who.ini')
        open(config_file, 'w').close()
        return config_file

    def _callFUT(self, context,
                 config_file=None,
                 identifier_id='IDENTIFIER',
                 callback=None):
        from pyramid_who.zcml import repozewho2authenticationpolicy
        if config_file is None:
            config_file = self._makeWhoConfig()
        if callback is None:
            return repozewho2authenticationpolicy(context,
                                                config_file,
                                                identifier_id)
        return repozewho2authenticationpolicy(context,
                                              config_file,
                                              identifier_id,
                                              callback)

    def test_it_defaults(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from pyramid_who.whov2 import _null_callback
        self.config._set_authorization_policy(object())
        context = DummyZCMLContext(self.config)
        self._callFUT(context)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['args'], ())
        regadapt['callable']()
        reg = self.config.registry
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy._identifier_id, 'IDENTIFIER')
        self.assertEqual(policy._callback, _null_callback)

    def test_it(self):
        from pyramid.interfaces import IAuthenticationPolicy
        context = DummyZCMLContext(self.config)
        self.config._set_authorization_policy(object())
        def _callback(identity, request):
            """ """ # hide from coverage
        config_file = self._makeWhoConfig('firstbase.ini')
        self._callFUT(context, config_file, 'something', _callback)
        actions = context.actions
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['args'], ())
        regadapt['callable']()
        reg = self.config.registry
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy._config_file, config_file)
        self.assertEqual(policy._identifier_id, 'something')
        self.assertEqual(policy._callback, _callback)

from pyramid.config import Configurator

class DummyZCMLContext(object):
    config_class = Configurator
    introspection = False
    def __init__(self, config):
        self.registry = config.registry
        self.package = config.package
        self.autocommit = config.autocommit
        self.route_prefix = getattr(config, 'route_prefix', None)
        self.basepath = getattr(config, 'basepath', None)
        self.includepath = getattr(config, 'includepath', ())
        self.info = getattr(config, 'info', '')
        self.actions = config._ctx.actions
        self._ctx = config._ctx

    def action(self, *arg, **kw): # pragma: no cover
        self._ctx.action(*arg, **kw)
