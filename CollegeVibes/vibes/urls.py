from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Home page
    path("login/", views.login_view, name="login"),  # User login
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),  # User registration
    
    # urls.py
    path('upload_students/', views.upload_students, name='upload_students'),
    path('create_students/', views.create_students, name='create_students'),

    path("master_login/", views.master_login, name="master_login"),  # Master login
    path("master_dashboard/", views.master_dashboard, name="master_dashboard"),  # Master dashboard
    path("master_add_student/", views.master_add_student, name="master_add_student"), 
    path("register_club/", views.register_club, name="register_club"),  # Register new club
    path("edit_club/<int:club_id>/", views.edit_club, name="edit_club"),  # Edit club details
    path("view_clubs/", views.view_clubs, name="view_clubs"),  # View all clubs
    path("delete_club/<int:club_id>/", views.delete_club, name="delete_club"),  # Delete a club
    path('student_details/', views.student_details, name='student_details'),
    path('edit_student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('master_solo_event_registrations/', views.master_solo_event_registrations, name='master_solo_event_registrations'),
    path('master_group_event_registrations/', views.master_group_event_registrations, name='master_group_event_registrations'),
    path('master_view_results/', views.master_view_results, name='master_view_results'),
    path('master_students_attended/', views.master_students_attended, name='master_students_attended'),
    path('master_current_events/', views.master_current_events, name='master_current_events'),
    path('master_completed_events/',views.master_completed_events,name='master_completed_events'),
    
    path("club_login/", views.club_login, name="club_login"),
    path('club_dashboard/', views.club_dashboard, name='club_dashboard'),
    path('events/', views.manage_events, name='manage_events'),
    path('completed_events/',views.completed_events,name='completed_events'),
    path('solo_event_registrations/', views.solo_event_registrations, name='solo_event_registrations'),
    path('group_event_registrations/', views.group_event_registrations, name='group_event_registrations'),
    path('send_notifications/', views.send_notifications, name='send_notifications'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('is_attend/', views.is_attend, name='is_attend'),
    path('students_attended/', views.students_attended, name='students_attended'),
    path('events/verify_payment/', views.verify_payment, name='verify_payment'),
    path('events/verify_payment/<int:registration_id>/', views.verify_payment, name='verify_payment'),
    path('mark_results/', views.mark_results, name='mark_results'),
    path('view_results/', views.view_results, name='view_results'),

    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path("register_event/<int:event_id>/", views.register_event, name="register_event"),
    path("unregister_event/<int:event_id>/", views.unregister_event, name="unregister_event"),
    path('registered_events/', views.registered_events, name='registered_events'),
    path('group_registration/<int:event_id>/', views.group_registration, name='group_registration'),
    path('register-group-event/<int:event_id>/', views.register_group_event, name='register_group_event'),

    path('myprofile/', views.myprofile, name='myprofile'),
    path('change_password/', views.change_password, name='change_password'),
    path("notifications/",views.notifications, name="notifications"),
    path('generate_certificates/', views.generate_certificates_view, name='generate_certificates'),
]
