import unittest


class TestRepozeWhowAuthenticationPolicyDirective(unittest.TestCase):

    _tempdir = None

    def setUp(self):
        from pyramid.testing import setUp
        self.config = setUp(autocommit=False)
        self.config._ctx = self.config._make_context()

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
        reg = self.config.registry
        context = self.config._ctx
        self._callFUT(context)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy._identifier_id, 'IDENTIFIER')
        self.assertEqual(policy._callback, _null_callback)

    def test_it(self):
        reg = self.config.registry
        from pyramid.interfaces import IAuthenticationPolicy
        context = self.config._ctx
        def _callback(identity, request):
            """ """ # hide from coverage
        config_file = self._makeWhoConfig('firstbase.ini')
        self._callFUT(context, config_file,
                      'something', _callback)
        actions = extract_actions(context.actions)
        self.assertEqual(len(actions), 1)
        regadapt = actions[0]
        self.assertEqual(regadapt['discriminator'], IAuthenticationPolicy)
        self.assertEqual(regadapt['callable'], None)
        self.assertEqual(regadapt['args'], ())
        policy = reg.getUtility(IAuthenticationPolicy)
        self.assertEqual(policy._config_file, config_file)
        self.assertEqual(policy._identifier_id, 'something')
        self.assertEqual(policy._callback, _callback)


def extract_actions(native):
    from zope.configuration.config import expand_action
    L = []
    for action in native:
        (discriminator, callable, args, kw, includepath, info, order
         ) = expand_action(*action)
        d = {}
        d['discriminator'] = discriminator
        d['callable'] = callable
        d['args'] = args
        d['kw'] = kw
        d['order'] = order
        L.append(d)
    return L
