from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home),
    path('talent/', views.talent, name = 'talent'),
    path('profile/', views.profile),
    path('employer/', views.employer),
    path('jobs/', views.jobs),
    path('studentdash/', views.studentdash),
    path('aboutus/', views.aboutus),
    path('studenterror/', views.studenterror),
    path('employererror/', views.employererror),
    path('jobedit/', views.jobedit, name = 'jobedit'),
    path('confirmdelete/<int:id>/', views.delete_job, name = 'confirmdelete'),
    path('edit_job/<int:id>/', views.edit_job, name='edit_job'),
    path('employer_list/', views.employer_list, name='employer_list'),
    path('studentinstructions/', views.studentinstructions, name='studentinstructions'),
    path('employerinstructions/', views.employerinstructions, name='employerinstructions')
]