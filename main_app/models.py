from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
# Create your models here.
SITES = (
	('O', 'On-Site'),
	('R', 'Remote'),
	('H', 'Hybrid'),
)
# Create your models here.
class Application(models.Model):
	name = models.CharField(max_length=100)
	role = models.CharField(max_length=100)
	salary = models.CharField(max_length=250)
	location = models.CharField(max_length=250)
	site = models.CharField(
		max_length=1,
		#choices
		choices=SITES,
		default=SITES[0][0]
	)