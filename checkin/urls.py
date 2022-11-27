from django.urls import path

from checkin import views


app_name = "checkin"

urlpatterns = [
    path("", views.HomeView.as_view(), name="HomeView"),
    path("register/", views.RegisterView.as_view(), name="RegisterView"),
    path("checkin/", views.CheckinHomeView.as_view(), name="CheckinHomeView"),
    path("checkin/my/", views.MyCheckinView.as_view(), name="MyCheckinView"),
    path("checkin/my/reports/", views.MyReportsView.as_view(), name="MyReportsView"),
    path("checkin/delete/<int:pk>/", views.DeleteCheckinView.as_view(), name="DeleteCheckinView"),
]
