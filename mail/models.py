from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Email(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='all_emails')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipients = models.ManyToManyField(User, related_name='received_emails')
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    def serialize(self):
        return {
            'id': self.id,
            'sender': self.sender.email,
            'recipients': [user.email for user in self.recipients.all()],
            'subject': self.subject,
            'body': self.body,
            'timestamp': self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            'read': self.read,
            'archive': self.archive
        }
