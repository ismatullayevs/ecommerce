from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from .models import Category, Item, OrderItem, Order


class CategoryMixin:
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['categories'] = Category.objects.all()[:6]
		return context


class HomeView(CategoryMixin, ListView):
    model = Item
    paginate_by = 8
    template_name = "home-page.html"



def checkout(request):
	return render(request, 'checkout-page.html')



class CategoryListView(CategoryMixin, ListView):
    model = Item
    paginate_by = 8
    template_name = "home-page.html"

    def get_queryset(self):
    	category = get_object_or_404(Category, slug=self.kwargs["slug"])
    	return category.item_set.all()

    def get_context_data(self, *args, **kwargs):
    	context = super().get_context_data(*args, **kwargs)
    	category = get_object_or_404(Category, slug=self.kwargs["slug"])
    	context['active_link'] = category.id
    	return context


class ProductDetailView(DetailView):
	model = Item
	template_name = "product-page.html"

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		item = Item.objects.get(slug=self.kwargs["slug"])
		category = item.category
		context['related_items'] = category.item_set.exclude(id=item.id)[:3]
		if self.request.user.is_authenticated:
			order_qs = Order.objects.filter(user=self.request.user, ordered=False)
			if order_qs.exists():
				order = order_qs[0]
				order_item = order.items.filter(user=self.request.user, item=item, ordered=False)
				if order_item.exists():
					context["already_added"] = True
		return context


class OrderSummaryView(LoginRequiredMixin, ListView):
	model = OrderItem
	template_name = "order_summary.html"

	def get_queryset(self):
		order, created = Order.objects.get_or_create(user=self.request.user, ordered=False)
		return order.items.all()

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		order = Order.objects.get(user=self.request.user, ordered=False)
		context["order"] = order
		return context


class AddToCartView(LoginRequiredMixin, View):
	def get(self, request, slug):
		item = get_object_or_404(Item, slug=slug)
		order_item, created = OrderItem.objects.get_or_create(
			item=item,
			user=request.user,
			ordered=False
		)
		try:
			order = Order.objects.get(user=request.user, ordered=False)
			if order.items.filter(item__slug=item.slug).exists():
				order_item.quantity += 1
				order_item.save()
				return redirect("order_summary")
			else:
				order.items.add(order_item)
				messages.success(request, "This item was added to the cart")
			return redirect("order_summary")
		except Order.DoesNotExist:
			order = Order.objects.create(user=request.user)
			order.items.add(order_item)
			messages.success(request, "This item was added to the new cart")
			return redirect("order_summary")


class RemoveFromCartView(LoginRequiredMixin, View):
	def get(self, request, slug):
		item = get_object_or_404(Item, slug=slug)
		try:
			order_item = OrderItem.objects.get(user=request.user, item=item, ordered=False)

		except OrderItem.DoesNotExist:
			messages.warning(request, "This item is not in your cart")
			return redirect("order_summary")

		try:
			order = Order.objects.get(user=request.user, ordered=False)
		except Order.DoesNotExist:
			order_item.delete()
			messages.warning(request, "You don't have an active order")
			return redirect("order_summary")


		order.items.remove(order_item)
		order_item.delete()
		messages.success(request, "Item was removed from your cart")
		return redirect('order_summary')



class RemoveSingleItemFromCartView(LoginRequiredMixin, View):
	def get(self, request, slug):
		item = get_object_or_404(Item, slug=slug)
		try:
			order_item = OrderItem.objects.get(user=request.user, item=item, ordered=False)

		except OrderItem.DoesNotExist:
			messages.warning(request, "This item is not in your cart")
			return redirect("order_summary")

		try:
			order = Order.objects.get(user=request.user, ordered=False)
		except Order.DoesNotExist:
			order_item.delete()
			messages.warning(request, "You don't have an active order")
			return redirect("order_summary")

		if order_item.quantity <= 1:
			order_item.delete()
		else:	
			order_item.quantity -= 1
			order_item.save()

		return redirect("order_summary")



class SearchView(ListView):
	model = Item
	paginate_by = 8
	def get_queryset(self):
		queryset = super().get_queryset()
		q = self.request.GET.get("q", None)
		items = queryset.filter(
			Q(title__icontains=q) | Q(description__icontains=q)
		).distinct()
		return items

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["q"] = self.request.GET.get("q", None)
		return context

	template_name = "results.html"
