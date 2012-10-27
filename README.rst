========
tinysmtp
========

Flask-Mail provides a nice interface to send email via SMTP. Unfortunately,
it's tightly coupled to the Flask app object making it difficult to run
outside of an app context.

This is a minimal subset of Flask-Mail that can run without an app-context.


Example::

  with Connection('myhost', port=25) as conn:
    msg = Message('alice@example.com', ['bob@example.com'], 'Subject',
                  body='body')
    conn.send(msg)
