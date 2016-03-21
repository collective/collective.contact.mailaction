# -*- coding: utf-8 -*-
from collective.contact.mailaction.interfaces import \
    ICollectiveContactMailactionTemplate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import formatdate
from plone import api
from plone.api.exc import InvalidParameterError
from zope import component

import email
import formatter
import htmllib
import logging
import StringIO


PATTERN = '************/'

logger = logging.getLogger('collective.contact.mailaction')


class Composer(object):
    """ This is somehow the view of the template.
    """

    context = None

    @property
    def request(self):
        return api.portal.get().REQUEST

    def render_template(self, template_name, items, vars):
        template = component.getUtility(
            ICollectiveContactMailactionTemplate,
            name=template_name
        )

        html = template(
            self,
            contents=[i[0] for i in items],
            items=[dict(formatted=i[0], original=i[1]) for i in items],
            **vars  # Tal options
        )

        return html


def create_email_body(html, text=None, headers=None):
    """Create a mime-message that will render HTML in popular
    MUAs, text in better ones.

    adapted collective.singing standard to strip style definitions off the
    plain text version
    """

    # Use DumbWriters word wrapping to ensure that no text line
    # is longer than plain_text_maxcols characters.
    plain_text_maxcols = 72

    try:
        encoding = api.portal.get_registry_record('plone.email_charset')
    except InvalidParameterError:
        encoding = api.portal.get().getProperty('email_charset', 'utf-8')

    html = html.encode(encoding)

    if text is None:
        # Produce an approximate textual rendering of the HTML string,
        # unless you have been given a better version as an argument
        textout = StringIO.StringIO()
        formtext = formatter.AbstractFormatter(
            formatter.DumbWriter(
                textout,
                plain_text_maxcols
            )
        )
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()

        # append the anchorlist at the bottom of a message
        # to keep the message readable.
        counter = 0
        anchorlist = "\n\n" + ("-" * plain_text_maxcols) + "\n\n"
        for item in parser.anchorlist:
            counter += 1
            anchorlist += "[%d] %s\n" % (counter, item)

        text = textout.getvalue() + anchorlist
        del textout, formtext, parser, anchorlist

        # strip off style definitions
        pos = text.find(PATTERN)
        if pos != -1:
            text = text[pos + len(PATTERN):]

    else:
        text = text.encode(encoding)

    # if we would like to include images in future, there should
    # probably be 'related' instead of 'mixed'
    msg = MIMEMultipart('mixed')
    msg['Date'] = formatdate(localtime=True)
    msg["Message-ID"] = email.Utils.make_msgid()
    if headers:
        for key, value in headers.items():
            msg[key] = value
    msg.preamble = 'This is a multi-part message in MIME format.'

    alternatives = MIMEMultipart('alternative')
    msg.attach(alternatives)
    alternatives.attach(MIMEText(text, 'plain', _charset=encoding))
    alternatives.attach(MIMEText(html, 'html', _charset=encoding))

    return msg
