from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("get-month", views.get_data_month, name="get-month"),
    path("user/<int:user_id>", views.month_page, name="month_page"),
    path("user/<int:user_id>/date", views.day_page, name="day-page"),
    path("add-event", views.add_event, name="add_event"),
    path("delete-event", views.delete_event, name="delete_event"),
    path("profile/<int:user_id>", views.profile_page, name="profile_page"),
    path("following", views.following, name="following"),
    path("change-follower/<int:user_id>", views.change_follower, name="change_follower"),
    path("search", views.search, name="search"),
    path("search_input", views.search_input, name="search_input"),
    path("delete_follower", views.delete_follower, name="delete_follower"),
    path("change_profile_page", views.change_profile_page, name="change_profile_page"),
]
