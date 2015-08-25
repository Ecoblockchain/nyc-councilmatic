from django.db import models


class Person(models.Model):
	ocd_id = models.CharField(max_length=100, unique=True)
	name = models.CharField(max_length=100)
	headshot = models.CharField(max_length=255, blank=True)
	source_url = models.CharField(max_length=255)
	source_note = models.CharField(max_length=255, blank=True)
	slug = models.CharField(max_length=255, unique=True)

	def __str__(self):
		return self.name

	@property
	def council_seat(self):
		return self.memberships.filter(organization__ocd_id='ocd-organization/389257d3-aefe-42df-b3a2-a0d56d0ea731').first().post.label

	@property
	def is_speaker(self):
		return True if self.memberships.filter(role='Speaker').first() else False	

	@property
	def headshot_url(self):
		if self.headshot:
			return '/static/images/' + self.ocd_id + ".jpg"
		else:
			return '/static/images/headshot_placeholder.png'

class Bill(models.Model):
	ocd_id = models.CharField(max_length=100, unique=True)
	description = models.TextField()
	identifier = models.CharField(max_length=50)
	bill_type = models.CharField(max_length=50)
	classification = models.CharField(max_length=100)
	date_created = models.DateTimeField(default=None)
	date_updated = models.DateTimeField(default=None, null=True)
	source_url = models.CharField(max_length=255)
	source_note = models.CharField(max_length=255, blank=True)
	from_organization = models.ForeignKey('Organization', related_name='bills', null=True)
	full_text = models.TextField(blank=True)
	last_action_date = models.DateTimeField(default=None, null=True)
	slug = models.CharField(max_length=255, unique=True)

	def __str__(self):
		return self.friendly_name

	@property
	def current_org(self):
		return self.actions.all().order_by('-date').first().organization if self.actions.all() else None

	@property
	def current_action(self):
		return self.actions.all().order_by('-date').first() if self.actions.all() else None

	@property
	def friendly_name(self):
		nums_only = self.identifier.split(' ')[-1]
		return self.bill_type+' '+nums_only

class Organization(models.Model):
	ocd_id = models.CharField(max_length=100, unique=True)
	name = models.CharField(max_length=255)
	classification = models.CharField(max_length=255, null=True)
	parent = models.ForeignKey('self', related_name='children', null=True)
	slug = models.CharField(max_length=255, unique=True)

	def __str__(self):
		return self.name

	@classmethod
	def committees(cls):
		return cls.objects.filter(classification='committee').order_by('name').all()

	@property
	def recent_activity(self):
		return self.actions.all().order_by('-date') if self.actions.all() else None

	@property
	def chairs(self):
		return self.memberships.filter(role='CHAIRPERSON')

class Action(models.Model):
	date = models.DateTimeField(default=None)
	classification = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	organization = models.ForeignKey('Organization', related_name='actions', null=True)
	bill = models.ForeignKey('Bill', related_name='actions', null=True)
	order = models.IntegerField()

	@property 
	def label(self):
		c = self.classification
		
		if c == 'committee-passage': return 'success'
		if c == 'passage': return 'success'
		if c == 'executive-signature': return 'success'
		if c == 'amendment-passage': return 'success'

		if c == 'amendment-introduction': return 'info'
		if c == 'introduction': return 'info'
		if c == 'committee-referral': return 'info'
		if c == 'filing': return 'info'
		if c == 'executive-received': return 'info'

		if c == 'deferred': return 'primary'

		else: return 'info'

class Post(models.Model):
	ocd_id = models.CharField(max_length=100, unique=True)
	label = models.CharField(max_length=255)
	role = models.CharField(max_length=255)
	organization = models.ForeignKey('Organization', related_name='posts')

class Membership(models.Model):
	organization = models.ForeignKey('Organization', related_name='memberships')
	person = models.ForeignKey('Person', related_name='memberships')
	post = models.ForeignKey('Post', related_name='memberships', null=True)
	label = models.CharField(max_length=255, blank=True)
	role = models.CharField(max_length=255, blank=True)
	start_date = models.DateField(default=None, null=True)
	end_date = models.DateField(default=None, null=True)

class Sponsorship(models.Model):
	bill = models.ForeignKey('Bill', related_name='sponsorships')
	person = models.ForeignKey('Person', related_name='sponsorships')
	classification = models.CharField(max_length=255)
	is_primary = models.BooleanField(default=False)

class Documents(models.Model):
	bill = models.ForeignKey('Bill', related_name='documents')
	note = models.TextField()
	url = models.TextField()

class LegislativeSession(models.Model):
	identifier = models.CharField(max_length=255)
	organization = models.ForeignKey('Organization', related_name='legislative_sessions')
	name = models.CharField(max_length=255)


