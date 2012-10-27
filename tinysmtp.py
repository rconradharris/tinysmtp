import smtplib
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid


class Connection(object):
    def __init__(self, hostname, port=25, username=None, password=None,
                 ssl=False, tls=False, debug=False):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssl = ssl
        self.tls = tls
        self.debug = debug

    def connect(self):
        SMTP = smtplib.SMTP_SSL if self.ssl else smtplib.SMTP
        self.connection = SMTP(self.hostname, self.port)
        self.connection.set_debuglevel(self.debug)
        if self.tls:
            self.connection.starttls()
        self.connection.login(self.username, self.password)

    def send(self, msg):
        self.connection.sendmail(msg.sender, msg.send_to, msg.as_string())

    def close(self):
        self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class Message(object):

    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message

    Source: Flask-Mail by Dan Jacob
    """
    def __init__(self, sender, subject,
                 recipients=None,
                 body=None,
                 html=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None):

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html
        self.date = date
        self.msgId = make_msgid()
        self.charset = charset
        self.extra_headers = extra_headers

        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to

        if recipients is None:
            recipients = []

        self.recipients = list(recipients)

        if attachments is None:
            attachments = []

        self.attachments = attachments

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def _mimetext(self, text, subtype='plain'):
        """
        Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def as_string(self):
        """
        Creates the email
        """

        if len(self.attachments) == 0 and not self.html:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body)
        elif len(self.attachments) > 0 and not self.html:
            # No html and at least one attachment means multipart
            msg = MIMEMultipart()
            msg.attach(self._mimetext(self.body))
        else:
            # Anything else
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(self._mimetext(self.body, 'plain'))
            alternative.attach(self._mimetext(self.html, 'html'))
            msg.attach(alternative)

        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients)

        msg['Date'] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        msg['Message-ID'] = self.msgId

        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)

        if self.cc:
            msg['Cc'] = ', '.join(self.cc)

        if self.reply_to:
            msg['Reply-To'] = self.reply_to

        if self.extra_headers:
            for k, v in self.extra_headers.iteritems():
                msg[k] = v

        for attachment in self.attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            f.add_header('Content-Disposition', '%s;filename=%s' %
                         (attachment.disposition, attachment.filename))

            for key, value in attachment.headers:
                f.add_header(key, value)

            msg.attach(f)

        return msg.as_string()

    def __str__(self):
        return self.as_string()

    def has_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        reply_to = self.reply_to or ''
        for val in [self.subject, self.sender, reply_to] + self.recipients:
            for c in '\r\n':
                if c in val:
                    return True
        return False

    def send(self, connection):
        """
        Verifies and sends the message.
        """

        assert self.recipients, "No recipients have been added"
        assert self.body or self.html, "No body or HTML has been set"
        assert self.sender, "No sender address has been set"

        if self.has_bad_headers():
            raise BadHeaderError

        connection.send(self)

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None):

        """
        Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """
        self.attachments.append(
            Attachment(filename, content_type, data, disposition, headers))
