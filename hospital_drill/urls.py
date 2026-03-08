from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('trainer/', views.trainer_dashboard, name='trainer_dashboard'),
    path('trainer/start/', views.start_simulation, name='start_simulation'),
    path('trainer/pause/', views.pause_resume_simulation, name='pause_resume_simulation'),
    path('trainer/reset/', views.reset_simulation, name='reset_simulation'),
    path('drill/<str:role>/', views.participant_view, name='participant_view'),
    path('api/updates/', views.check_updates, name='check_updates'),
    path('api/submit/', views.submit_decision, name='submit_decision'),
    path('report/', views.report_view, name='report_view'),
]
