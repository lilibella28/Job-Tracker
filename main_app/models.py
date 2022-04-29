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
	# internally it will be cat_id the _id automatically gets added
	application = models.ForeignKey(Application, on_delete=models.CASCADE)

	def __str__(self):
		# this method will gives us the friendly meal choices value, so like Breakfast instead of B
		return f"note {self.name} on {self.date}"

	class Meta:
		ordering = ['-date']

class Photo(models.Model):
    url = models.CharField(max_length=200)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
  

    def __str__(self):
        return f"Photo for application_id: {self.application_id} @{self.url}" 