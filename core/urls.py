from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomeView.as_view(), name="home_page"),
	path('categories/<slug>/', views.CategoryListView.as_view(), name="by_category"),
	path('producs/<slug>/', views.ProductDetailView.as_view(), name="product_detail"),
	path('add_to_cart/<slug>/', views.AddToCartView.as_view(), name="add_to_cart"),
	path('remove_from_cart/<slug>/', views.RemoveFromCartView.as_view(), name="remove_from_cart"),
	path('remove_single_item_from_cart/<slug>/', views.RemoveSingleItemFromCartView.as_view(), name="remove_single_item_from_cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('order-summary/', views.OrderSummaryView.as_view(), name="order_summary"),
	path('search', views.SearchView.as_view(), name="search"),
]