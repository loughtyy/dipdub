from store.forms import LoginForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.views.generic.base import RedirectView 

app_name = 'store'

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"), 
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),
    path('plus-cart/<int:cart_id>/', views.plus_cart, name="plus-cart"),
    path('minus-cart/<int:cart_id>/', views.minus_cart, name="minus-cart"),
    path('update-cart/<int:cart_id>/', views.update_cart_quantity, name='update-cart'),
    path('cart/', views.cart, name="cart"),
    path('toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('checkout/', views.checkout, name="checkout"),
    path('orders/', views.orders, name="orders"),

    path('news/', views.news_list, name="news_list"),
    path('news/<slug:slug>/', views.news_detail, name="news_detail"),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    path('product/<slug:slug>/', views.detail, name="product-detail"),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('categories/', views.all_categories, name="all-categories"),
    path('<slug:slug>/', views.category_products, name="category-products"),

    path('accounts/register/', views.RegistrationView.as_view(), name="register"),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html', authentication_form=LoginForm), name="login"),
    path('accounts/profile/', views.profile, name="profile"),
    path('accounts/add-address/', views.AddressView.as_view(), name="add-address"),
    path('accounts/remove-address/<int:id>/', views.remove_address, name="remove-address"),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),

    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='account/password_change.html', form_class=PasswordChangeForm, success_url='/accounts/password-change-done/'), name="password-change"),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name="password-change-done"),

    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html', form_class=PasswordResetForm, success_url='/accounts/password-reset/done/'), name="password-reset"),
    path('accounts/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name="password_reset_done"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html', form_class=SetPasswordForm, success_url='/accounts/password-reset-complete/'), name="password_reset_confirm"),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name="password_reset_complete"),
]

urlpatterns += [
    path('media/<path:path>', RedirectView.as_view(url='/static/%(path)s'), name='media_redirect'),
]
