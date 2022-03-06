from django.conf import settings
from django.db import models
from slugify import slugify
from django.urls import reverse
import uuid
from datetime import datetime
from django_countries.fields import CountryField


LABEL = (
	("N", "New"),
	("T", "Top"),
)

ADDRESS_TYPES = (
	("S", "Shipping"),
	("B", "Billing"),
)

class Item(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	title = models.CharField(max_length=100)
	brand = models.CharField(max_length=20, blank=True, null=True)
	description = models.TextField(max_length=300)
	label = models.CharField(max_length=1, choices=LABEL, blank=True, null=True)
	image = models.ImageField(upload_to="product_images")
	slug = models.SlugField(max_length=70,  blank=True, null=True, unique=True)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	discount_price = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		now = datetime.now()
		if not self.slug:
			self.slug = slugify(self.title + "-" + now.strftime("%f"))

		return super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse("product_detail", args=(self.slug,))


	def get_item_price(self):
		if self.discount_price:
			return self.price - self.discount_price
		return self.price


	class Meta:
		ordering = ('-date_added',)


class Category(models.Model):
	name = models.CharField(max_length=30)
	slug = models.SlugField(unique=True, blank=True, null=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)

		return super().save(*args, **kwargs)


class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="items")
	item = models.OneToOneField(Item, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return self.item.title


	def get_total_item_price(self):
		return self.item.get_item_price() * self.quantity

	def get_total_discount_price(self):
		if self.item.discount_price:
			return self.item.discount_price * self.quantity
		return 0



class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
	items = models.ManyToManyField(OrderItem)
	date_started = models.DateTimeField(auto_now_add=True)
	date_ordered = models.DateTimeField(blank=True, null=True)
	ordered = models.BooleanField(default=False)
	shipping_address = models.OneToOneField("Address", on_delete=models.CASCADE, blank=True, null=True, related_name="shipping_address")
	billing_address = models.OneToOneField("Address", on_delete=models.CASCADE, blank=True, null=True, related_name="billing_address")
	being_delivered = models.BooleanField(default=False)
	received = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)
	
	def get_total(self):
		total = 0
		for item in self.items.all():
			total += item.get_total_item_price()

		return total


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	street_address = models.CharField(max_length=100)
	apartment_address = models.CharField(max_length=100)
	country = CountryField(multiple=False)
	zip_code = models.CharField(max_length=32)
	address_type = models.CharField(max_length=1, choices=ADDRESS_TYPES)
	default = models.BooleanField(default=False)

	def __str__(self):
		return self.street_address