from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('rejected/', views.rejected, name='rejected-applications'),
    path('later_on/', views.later_on, name='later-applications'),
    path('mpesa/', views.mpesa, name='mpesa'),
    path('student-card', views.student, name="student-card"),
    path('responses', views.separation, name="responses"),
    path('applications', views.applications, name="applications"),
    path('add-teacher', views.add_teacher, name="add-teacher"),
    path('add-student', views.add_student_view, name="add-student"),
    path('course_view', views.course_view, name="course_view"),
    path('class-pdf', views.getPdfPage, name="class-pdf"),
    path('crmpage/apps_edit/<int:pk>/<str:model_type>/', views.apps_edit, name='apps_edit'),  # Corrected path
    path('crmpage/sheet2_edit/<int:pk>/', views.apps_edit, {'model_type': 'sheet2application'}, name='sheet2_edit'),
    path('edit_results/<int:candidate_id>/', views.edit_results, name='edit_results'),
    path('login', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"),
    path('logout', views.logoutUser, name="logout"),
    path('success', views.success, name='success'),
    path('updated-candidates', views.updated_candidate, name='updated-candidates'),
    path('add-application', views.add_applications, name='add-application'),
    path('status-edit/(?P<pk>\d+)', views.status_edit, name='status-edit/(?P<pk>\d+)'),
    path('add-candidate', views.add_candidate, name='add-candidate'),
    path('update_database/', views.update_database, name='update_database'),
    path('update_sheet2_database/', views.update_sheet2_database, name='update-database'),
    path('model', views.model, name='model'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/<int:candidate_id>/', views.candidate_detail, name='candidate_detail'),
    path('generate_invoice/<int:candidate_id>/', views.generate_invoice, name='generate_invoice'),
    path('candidates/<int:candidate_id>/upload_contract/', views.upload_contract, name='upload_contract'),
    path('record-attendance/<int:candidate_id>/', views.record_attendance, name='record_attendance'),
    path('record-attendance/', views.record_attendance, name='record_attendance'),
    path('attendance-details/', views.attendance_details, name='attendance_details'),
    path('attendance-details/<int:candidate_id>/', views.attendance_details, name='attendance_details'),

]
