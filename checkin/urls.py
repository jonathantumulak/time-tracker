from django.urls import path

from checkin import views


app_name = "checkin"

urlpatterns = [
    path("", views.HomeView.as_view(), name="HomeView"),
    path("register/", views.RegisterView.as_view(), name="RegisterView"),
    path("checkin/", views.CheckinHomeView.as_view(), name="CheckinHomeView"),
    path("checkin/list/", views.ListCheckinView.as_view(), name="ListCheckinView"),
]
