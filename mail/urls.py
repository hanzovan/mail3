from django.urls import path
from . import views

app_name = 'mail'

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),

    # API routes
    path('emails', views.compose, name='compose'),
    
    path('emails/mail_content/<int:email_id>', views.email, name='email'),

    path('emails/mail_list/<str:mailbox>', views.mailbox, name='mailbox')

    # These 2 lines can cause bad requesting error,
    # because they have similar route
    # path('emails/<int:email_id>', views.email, name="email"),
    # path('emails/<str:mailbox>', views.mailbox, name='mailbox')    
]
