# -*- coding: utf-8 -*-
from .interfaces import ICollectiveContactMailactionTemplate
from email.utils import formataddr
from plone import api
from zope.component import getUtilitiesFor
from zope.interface.declarations import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def TemplatesVocabulary(context):
    adapters = getUtilitiesFor(ICollectiveContactMailactionTemplate)

    terms = []
    for adTuple in adapters:
        terms.append(SimpleTerm(
            value=adTuple[0],
            token=adTuple[0].encode('utf-8'),
            title=adTuple[0]
        ))

    return SimpleVocabulary(terms)

directlyProvides(TemplatesVocabulary, IVocabularyFactory)


def MailSenderVocabulary(context):

    items = {}

    # Portal/global E-Mail Address
    portal = api.portal.get()
    items[portal.email_from_address] = formataddr((
        portal.email_from_name,
        portal.email_from_address,
    ))

    # The current authenticated Members E-Mail.
    member = api.user.get_current()
    if member:
        email = member.getProperty("email")
        if email != u"":
            items[email] = formataddr((
                member.getProperty("fullname"),
                email,
            ))

    terms = []
    for _id, title in items.iteritems():
        terms.append(SimpleTerm(
            value=_id,
            token=_id.encode('utf-8'),
            title=title
        ))

    return SimpleVocabulary(terms)

directlyProvides(MailSenderVocabulary, IVocabularyFactory)
