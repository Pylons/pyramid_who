from zope.interface import directlyProvides
from repoze.who.interfaces import IChallengeDecider

def forbidden_challenger(environ, status, headers):
    return status.startswith('403 ')
directlyProvides(forbidden_challenger, IChallengeDecider)
