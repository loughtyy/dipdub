import sys
from django.core.mail.backends.console import EmailBackend

class ReadableConsoleEmailBackend(EmailBackend):
    def write_message(self, message):
        subject = message.subject
        to = ', '.join(message.to)
        
        if message.body:
            if isinstance(message.body, bytes):
                body = message.body.decode('utf-8', errors='replace')
            else:
                body = message.body
        else:
            body = ''
            try:
                for part in message.alternatives:
                    if part[1] == 'text/plain':
                        body = part[0]
                        break
                if not body:
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='replace')
                            break
            except Exception:
                pass
        
        sys.stdout.write(f"Subject: {subject}\n")
        sys.stdout.write(f"To: {to}\n")
        sys.stdout.write(f"\n{body}\n")
        sys.stdout.write("-" * 60 + "\n")