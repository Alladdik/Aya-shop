from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Основні сторінки
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),

    # Продукти
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:pk>/', views.delete_product, name='delete_product'),

    # Категорії
    path('categories/', views.category_list, name='category_list'),  # Додано новий шлях для списку категорій
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:pk>/', views.delete_category, name='delete_category'),

    # Аутентифікація користувача
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Профіль користувача
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('accounts/profile/', views.profile, name='account_profile'),

    # Зміна пароля
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='change_password.html',
        success_url='/change-password/done/'
    ), name='change_password'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='change_password_done.html'
    ), name='password_change_done'),

    # Скидання пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),

    # Кошик
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Покупки
    path('checkout/', views.checkout, name='checkout'),
    path('purchases/', views.purchases, name='purchases'),
    path('product_content/<int:product_id>/', views.product_content, name='product_content'),

    # Баланс
    path('add_funds/', views.add_funds, name='add_funds'),
]