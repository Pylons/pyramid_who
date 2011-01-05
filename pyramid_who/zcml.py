from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import TextLine

from pyramid.config import Configurator
from pyramid_who.whov2 import WhoV2AuthenticationPolicy


class IRepozeWho2AuthenticationPolicyDirective(Interface):
    config_file = ASCIILine(title=u'config_file', required=True)
    identifier_name = TextLine(title=u'identitfier_name', required=True)
    callback = GlobalObject(title=u'callback', required=False)


def repozewho2authenticationpolicy(_context,
                                   config_file,
                                   identifier_name,
                                   callback=None):
    if callback is None:
        policy = WhoV2AuthenticationPolicy(config_file, identifier_name)
    else:
        policy = WhoV2AuthenticationPolicy(config_file, identifier_name,
                                           callback=callback)
    # authentication policies must be registered eagerly so they can
    # be found by the view registration machinery
    config = Configurator.with_context(_context)
    config._set_authentication_policy(policy)
