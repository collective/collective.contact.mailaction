# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.contact.core.content.held_position import IHeldPosition
from collective.contact.facetednav.browser.actions.base import BatchActionBase
from collective.contact.mailaction import _
from collective.contact.mailaction.adapters import IRecipientProvider
from collective.contact.mailaction.browser.actions.mail_utils import Composer
from collective.contact.mailaction.browser.actions.mail_utils import create_email_body
from collective.contact.mailaction.vocabularies import MailSenderVocabulary
from email.utils import formataddr
from plone import api
from plone.protect import PostOnly
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import interfaces
from zope import schema
from zope.interface import Interface


default_template = ViewPageTemplateFile('default_template.pt')


class MailBatchAction(BatchActionBase):

    label = _(u"label_mail_batch", default=u"Send mail to")
    name = 'mail'
    klass = 'context'
    weight = 500

    @property
    def onclick(self):
        return 'contactcontactmailsend.facetednav_send_mail()'

    def available(self):
        return True


class IMailSendForm(Interface):
    template = schema.Choice(
        title=_(u"form_template", default=u"Template:"),
        vocabulary='collective.contact.mailaction.templates',
    )

    reply_to = schema.Choice(
        title=_(u"form_reply_to", default=u"Reply To:"),
        vocabulary='collective.contact.mailaction.mailsender',
    )

    subject = schema.TextLine(
        title=_(u"form_subject", default=u"Subject:")
    )

    text = schema.Text(
        title=_(u"form_text", default=u"Text:"),
        description=_(
            u"form_text_help",
            default=u"You can use restructured text here."
        )
    )


class MailSendForm(form.Form):

    fields = field.Fields(IMailSendForm)
    ignoreContext = True
    ignoreRequest = False
    method = 'POST'

    uids = None

    def updateWidgets(self):
        self.uids = self.request.form.get('UID', None)
        if self.uids:
            self.fields += field.Fields(
                schema.TextLine(
                    __name__='uids_input',
                    title=u'contact uids',
                    required=False,
                    default=u','.join(self.uids)
                )
            )

        else:
            self.fields += field.Fields(
                schema.TextLine(
                    __name__='uids_input',
                    title=u'contact uids',
                    required=False
                )
            )

        super(MailSendForm, self).updateWidgets()
        self.widgets['uids_input'].mode = interfaces.HIDDEN_MODE
        self.widgets['text'].rows = 20

    @button.buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(_(u'button_send', default=u'Send'))
    def handleSave(self, action):
        statusmessages = IStatusMessage(self.request)

        PostOnly(self.request)
        data, errors = self.extractData()
        if errors:
            statusmessages.add(
                _(u"status_parse_error", default="Failed to parse the Form."),
                type="error"
            )
            return False

        portal_transforms = api.portal.get_tool(name='portal_transforms')
        transformed = portal_transforms.convertTo(
            'text/html',
            data['text'],
            mimetype='text/restructured',
        )

        portal = api.portal.get()
        vars = {
            'subject': data['subject'],
            'body': transformed.getData(),
            'site_url': portal.absolute_url(),
            'site_title': portal.Title(),
        }

        html = Composer().render_template(
            data["template"],
            {},
            vars,
        )

        portal = api.portal.get()
        sender_mail = formataddr((
            portal.email_from_name,
            portal.email_from_address,
        ))

        mailSVocab = MailSenderVocabulary(self.context)
        msg = create_email_body(html, headers={"Reply-To": mailSVocab.getTerm(data['reply_to']).title})

        if not self.uids:
            self.uids = data['uids_input'].split(',')

        mailcount = 0
        failed = []
        for uid in self.uids:
            obj = api.content.get(UID=uid)

            if obj:
                if IHeldPosition.providedBy(obj):
                    obj = IHeldPosition(obj).get_person()

                recipient = IRecipientProvider(obj)()
                if recipient is None:
                    failed.append(safe_unicode(obj.Title()))
                    continue

                api.portal.send_email(
                    recipient=recipient,
                    sender=sender_mail,
                    subject=data['subject'],
                    body=msg
                )
                mailcount += 1

        statusmessages.add(
            _(u"status_mail_send",
                default="Sent ${number} E-Mails.",
                mapping={"number": mailcount}),
            type="info"
        )

        if failed:
            statusmessages.add(
                _(u"status_mails_failed",
                    default="${num} contacts without email-address: ${names}",
                    mapping={'num': len(failed),
                             'names': u','.join(failed)}),
                type="warning"
            )

        self.request.response.redirect(self.context.absolute_url())

mailSelectionTemplate = ViewPageTemplateFile('mail.pt')
MailSelectionView = wrap_form(MailSendForm, index=mailSelectionTemplate)
