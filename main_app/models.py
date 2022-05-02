from os import link
from telnetlib import STATUS
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
 
# @receiver(user_signed_up)
# def after_user_signed_up(request, user, **kwargs):
# 	profile = Profile.objects.create(name=user.username) 
# 	print(profile)
# 	profile.save()

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100, blank=True)
	networks = models.ManyToManyField(User, related_name='networks', blank=True)
	intro = models.CharField(max_length=250, blank=True)
	title = models.CharField(max_length=100, blank=True)
	hobies = models.CharField(max_length=100, blank=True)
	def __str__(self):
		return f"This profile belongs to {self.user.username} with an id of {self.user_id}"
    
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
		print("Profile created")

# post_save.connect(create_profile, sender=User)

@receiver(post_save, sender=User)
def update_profile(sender, instance, created, **kwargs):
	if created == False:
		instance.profile.save()
		print("Profile Updated")

# post_save.connect(update_profile, sender=User)

class Network_Request(models.Model):
	from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
	to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)


SITES = (
        ('O', 'On-Site'),
        ('R', 'Remote'),
        ('H', 'Hybrid'),
)
# Create your models here.
STATUS = (
    ('Pending', 'Pending'),
    ('Moving Forward', 'Moving Forward'),
    ('Rejected', 'Rejected'),
)
# Create your models here.

class Application(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    salary = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    link = models.URLField(max_length=200)
    site = models.CharField(
        max_length=1,
        # choices
        choices=SITES,
        default=SITES[0][0]
    )
    status = models.CharField(
        max_length=15,
        # choices
        choices=STATUS,
        default=STATUS[0][0]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"The application named {self.name} has id of {self.id}"

    def get_absolute_url(self):
        return reverse('detail', kwargs={'application_id': self.id})


class Note(models.Model):
    date = models.DateField('note date')
    name = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    # the foregin key always goes on the many side
    # internally it will be application_id the _id automatically gets added
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    def __str__(self):
        return f"note {self.name} on {self.date}"

    class Meta:
        ordering = ['-date']


class Photo(models.Model):
    url = models.CharField(max_length=200)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for application_id: {self.application_id} @{self.url}"
