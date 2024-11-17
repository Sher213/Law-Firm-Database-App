from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),                      # Home page
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),           # Signup page
    path('execute_sql/', views.execute_sql, name='execute_sql'),  # SQL query page
    path('contact/', views.contact, name='contact'),       # Contact page

]
