from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('members/add/', views.add_member, name='add_member'),
    path('contributions/add/', views.add_contribution, name='add_contribution'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
    path('register/', views.register, name='register'),

    path('profile/', views.profile_view, name='profile'),

    # Placeholder for Update Profile (requires login)
    path('profile/edit/', login_required(lambda request: "TODO: Implement Update Profile"), name='update_profile'),

    path('register_member_view/', views.register_member_view, name='register_member_view'),

    path('logout/', views.logout_view, name='logout'),
]
