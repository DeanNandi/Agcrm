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
    path('crmpage/eldoret_edit/<int:pk>/<str:model_type>/', views.eldoret_edit, name='eldoret_edit'),  # Corrected path
    path('crmpage/sheet2_edit/<int:pk>/', views.apps_edit, {'model_type': 'sheet2application'}, name='sheet2_edit'),
    path('edit_results/<int:candidate_id>/', views.edit_results, name='edit_results'),
    path('login', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"),
    path('logout', views.logoutUser, name="logout"),
    path('success', views.success, name='success'),
    path('updated-candidates', views.updated_candidate, name='updated-candidates'),
    path('add-application', views.add_applications, name='add-application'),
    path('eldoret-application', views.add_eldored_applicant, name='eldoret-application'),
    path('enrolled_eldoret', views.enrolled_eldoret, name='enrolled_eldoret'),
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
    path('attendance-details/', views.attendance_details, name='attendance_details'),
    path('attendance-details/<int:candidate_id>/', views.attendance_details, name='attendance_details'),
    path('payment-history/', views.payment_history_view, name='payment_history'),
    path('unique-payment/<int:candidate_id>/', views.unique_payments, name='unique_payment'),
    path('class_attendance/', views.class_attendance_record, name='class_attendance_record'),
    path('fee_structure/', views.create_fee_structure, name='fee_structure'),
    path('create_discount/', views.create_discount, name='create_discount'),
    path('update_candidates/', views.update_candidates, name='update_candidates'),
    path('edit_candidate/<int:pk>/<str:model_type>/', views.edit_candidate, name='edit_candidate'),
    path('class_fee/new/<int:candidate_id>/', views.create_class_fee, name='class_fee_new'),
    path('month-range/update/<int:month_id>/', views.update_month_range, name='update_month_range'),
    # new paths
    path('update-fees/<int:candidate_id>/', views.update_school_fees, name='update_fees'),
    path('schoolfee/<int:pk>/add/', views.SchoolFeeCreate.as_view(), name='schoolfee_add'),
    path('schoolfee/<int:pk>/update/', views.SchoolFeeUpdate.as_view(), name='schoolfee_update'),
    path('schoolfee/<int:pk>/delete/', views.SchoolFeeDelete.as_view(), name='schoolfee_delete'),
    # new admissions
    path('generate_admissions/<int:candidate_id>/', views.generate_admission, name='generate_admissions'),
    # index attendance
    path('index/<int:year>/<int:month>/', views.index, name='index_with_month'),
    # new FeeStructure
    path('generate_fee_structure/<int:candidate_id>/', views.generate_course_fee, name='Generate_Fee_Structure'),


]
