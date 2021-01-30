from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('welcome', views.welcome, name = 'welcome'),
    path('getemployee', views.get_employees),
    path('addemployee', views.add_employee),
    path('updateemployee/<int:employee_id>', views.update_employee),
    path('deleteemployee/<int:employee_id>', views.delete_employee)
]