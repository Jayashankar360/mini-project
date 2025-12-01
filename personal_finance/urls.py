"""
URL configuration for personal_finance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('edit_transaction/<int:transaction_id>/', views.transaction_update, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:pk>/update/', views.goal_update, name='goal_update'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    path('analytics/', views.analytics, name='analytics'),
    path('profile/', views.profile, name='profile'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('verify_otp', views.verify_otp, name='verify_otp'),
    path('set_new_password', views.set_new_password, name='set_new_password'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
