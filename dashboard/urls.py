from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.home, name='home'),
    path('admin', views.admin, name='admin'),
    path('manager', views.manager, name='manager'),
    path('accountant', views.accountant, name='accountant'),
    path('accountant_list', views.accountant_list, name='accountant-list'),
    path("create_report", views.create_report, name="create_report"),
    path("edit-report/<id>", views.report_edit, name="report-edit"),
    path("approve_report/<id>", views.approve_report, name="approve_report"),
    path('reports/<int:id>/feedback/', views.collect_feedback, name='collect_feedback'),
    path('reports/feedback/<int:id>', views.get_accountant_feedback, name='view_feedback'),
    path('reports/feedback/resolve/<int:id>', views.resolve_feedback, name='resolve_feedback'),
    path('export', views.export_to_excel, name='export'),
    path('export/<int:id>', views.export_single_report_to_excel, name='export_report'),
]