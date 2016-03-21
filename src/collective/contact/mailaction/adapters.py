# -*- coding: utf-8 -*-
from collective.contact.core.behaviors import IContactDetails
from collective.contact.core.content.person import IPerson
from email.utils import formataddr
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface


class IRecipientProvider(Interface):
    pass


@implementer(IRecipientProvider)
class RecipientProvider(object):

    adapts(IPerson)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        cd = IContactDetails(self.context)
        return formataddr((
            "%s %s" % (self.context.firstname, self.context.lastname),
            cd.email,
        ))
