from flask import current_app
import envelopes


def send_async_email(app, toaddr, body):
    with app.app_context():
        conn = envelopes.SMTP(host=current_app.config['MAIL_HOST'],
                              port=current_app.config['MAIL_PORT'],
                              login=current_app.config['MAIL_LOGIN'],
                              password=current_app.config['MAIL_PASSWORD'],
                              tls=False,
                              timeout=None)

        envelope = envelopes.envelope.Envelope(to_addr=toaddr,
                                               from_addr=current_app.config['FROM_ADDR'],
                                               subject=current_app.config['REG_SUBJECT'],
                                               bcc_addr=current_app.config['ADMIN_EMAIL'],
                                               charset='utf-8',
                                               text_body=body)

        conn.send(envelope)
