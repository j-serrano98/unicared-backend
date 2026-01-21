from django.urls import path
# from .views import (
#     ProfileDetailView, ProfileSettingsView,
#     SelectCareerView, EnrollmentListView, EnrollmentUpdateView, ProfileStatsView,
#     TeacherList, TeacherDetail, TeacherReviewList,
#     CareerList, CareerDetail, SubjectList, SubjectDetail,
#     ReviewListCreateView,
#     UserList, UserDetail,
#     MeView, signup, login
#     )
from .views import *

urlpatterns = [

    # Authentication 
    path('auth/login/', login),
    path('auth/signup/', signup),
    # path('auth/me/', MeView.as_view()),
    
    # Profile
    path('profile/me/', ProfileDetailView.as_view()), # All information about the user profile
#     path('profile/settings/', ProfileSettingsView.as_view()), # Settings set by the user to the account

#     # Career & enrollments
    path('profile/career/', SelectCareerView.as_view()), # GET/POST profile career
    path('profile/enrollments/', EnrollmentListView.as_view()), # Get list of enrollments for the profile
    path('profile/enrollments/<int:pk>', EnrollmentUpdateView.as_view()), # Get details of enrollment
    path('profile/stats/', ProfileStatsView.as_view()), # Credits completed, GPA, progress, etc

#     # Teachers
    path('teachers/', TeacherListView.as_view()), # Get all teachers
    path('teachers/<uuid:uuid>/', TeacherDetailView.as_view()), # Get details of teacher
    # path('teachers/reviews/',)
#     path('teachers/<uuid:uuid>/reviews/', TeacherReviewList.as_view()), # Get all reviews by teacher

#     # Careers & subjects
    path('careers/', CareerListView.as_view()), # Get all careers
#     path('careers/<int:id>', CareerDetail.as_view()), # Get details of career
    path("subjects/", SubjectListView.as_view()), # Get all subjects
#     path("subjects/<int:pk>/", SubjectDetail.as_view()), # Get details of subject

#     # Users
#     path('users/', UserList.as_view()), # Get all users
#     path('users/<uuid:uuid>'), # Get details of user

#     # Reviews
#     path("reviews/",) # Get all reviews
]