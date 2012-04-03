from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import ASCIILine
from zope.schema import TextLine

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
    from pyramid_zcml import with_context
    config = with_context(_context)
    config.set_authentication_policy(policy)
