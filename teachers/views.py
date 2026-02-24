from rest_framework import generics, status
from .models import Teacher, Career, Enrollment, Profile, Subject, Review
# from .serializers import TeacherSerializer, CareerSerializer, UserSerializer, EnrollmentSerializer, SelectCareerSerializer
from rest_framework.views import APIView
from .serializers import *
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Avg, Count, F, FloatField, Sum, Q, FloatField
from django.db.models.functions import Cast
from dateutil.relativedelta import relativedelta


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

# class ProfileSettingsView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSettingsSerializer
#     permission_classes = [IsAuthenticated]

class SelectCareerView(generics.GenericAPIView):
    serializer_class = SelectCareerSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile
        first_name = request.user.first_name
        last_name = request.user.first_name
        career = get_object_or_404(Career, id=serializer.validated_data["career_id"])

        profile.career = career

        if first_name and last_name and profile.career:
            profile.onboarding_completed = True
        profile.save()

        existing_subject_ids = set(
            profile.enrollments.values_list("subject_id", flat=True)
        )

        enrollments_to_create = [
            Enrollment(
                student=profile,
                subject=subject,
                status=Enrollment.Status.NOT_TAKEN
            )
            for subject in career.subjects.all().order_by('id')
            if subject.id not in existing_subject_ids
        ]

        Enrollment.objects.bulk_create(enrollments_to_create)

        return Response(
            {"message": "Career selected and enrollments created"},
            status=status.HTTP_201_CREATED
        )

class EnrollmentListView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes =  [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class EnrollmentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes =  [IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user.profile)

# # EnrollmentUpdateView, 

class ProfileStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)

        stats_data = self.get_stats_context(profile)

        stats_data['current_rank'] = profile.current_rank

        serializer = ProfileStatsSerializer(stats_data)

        return Response(serializer.data)

    def get_stats_context(self, profile):
        
        enrollments = profile.enrollments.all()
        
        completion_rate = profile.get_completion_rate()

        first_enrollment = Enrollment.objects.filter(completion_date__isnull=False).order_by("completion_date")[:1].first()

        if first_enrollment:

            num_months = enrollments.count() 
            
            start_date = first_enrollment.completion_date.strftime("%B %Y")
            
            end_date_obj = first_enrollment.completion_date + relativedelta(months=num_months)
            end_date = end_date_obj.strftime("%B %Y")

        else:
            start_date = "Not Confirmed"
            end_date = "Not Confirmed"

        credits_data = enrollments.aggregate(
            total_credits=Sum('subject__credits'),
            completed_credits=Sum(
                'subject__credits', 
                filter=models.Q(grade__isnull=False)
            )
        )
        
        total_credits = credits_data['total_credits'] or 0
        credits_completed = credits_data['completed_credits'] or 0

        gpa_data = enrollments.filter(
                grade__isnull=False,
                subject__credits__isnull=False
            ).aggregate(
                total_points=Sum(
                    F("grade") * F("subject__credits"),
                    output_field=FloatField()
                ),
                total_credits=Sum("subject__credits"),
            )
        
        gpa = (
            gpa_data["total_points"] / gpa_data["total_credits"]
            if gpa_data["total_credits"]
            else None
        )

        print(enrollments)

        return {
            "start_date": start_date,

            "end_date": end_date,

            "gpa": gpa,

            "total_enrollments": enrollments.count(),

            "completed_enrollments": enrollments.filter(
                status=Enrollment.Status.COMPLETED
            ).count(),

            "total_reviews": enrollments.filter(
                    Q(review__punctuality__isnull=False) |
                    Q(review__clarity__isnull=False) |
                    Q(review__justice__isnull=False) |
                    Q(review__support__isnull=False) |
                    Q(review__flexibility__isnull=False) |
                    Q(review__knowledge__isnull=False) |
                    Q(review__methodology__isnull=False) |
                    Q(review__comment__isnull=False)
                ).distinct().count(),

            "total_credits": total_credits,

            "credits_completed": credits_completed,

            "credits_left": total_credits - credits_completed,

            "completion_rate": completion_rate,
        }

class TeacherListView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all().order_by('name').prefetch_related('enrollments__review', 'subjects', 'department')
    serializer_class = TeacherSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        queryset = Teacher.objects.annotate(
            total_reviews=Count('enrollments__review'),
            calculated_rating=Avg(
                (
                    Cast(F('enrollments__review__punctuality'), FloatField()) +
                    F('enrollments__review__clarity') +
                    F('enrollments__review__justice') +
                    F('enrollments__review__support') +
                    F('enrollments__review__flexibility') +
                    F('enrollments__review__knowledge') +
                    F('enrollments__review__methodology')
                ) / 7.0
            )
        ).prefetch_related('subjects', 'department')

        top_param = self.request.query_params.get('top')
        if top_param == 'true':
            return queryset.filter(total_reviews__gt=0).order_by('-calculated_rating')[:5]
        
        return queryset.order_by('calculated_rating')

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all().prefetch_related('enrollments__review', 'subjects', 'department')
    serializer_class = TeacherDetailSerializer
    lookup_field = 'slug'

# class TeacherReviewList(generics.ListCreateAPIView):
#     # queryset = Review.objects.filter(where current teacher)

class CareerListView(generics.ListCreateAPIView):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer


# class CareerDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Career.objects.all()
#     serializer_class = CareerSerializer
#     lookup_field = 'id'

class SubjectListView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Subject.objects.all()
#     serializer_class = SubjectSerializer
#     lookup_field = 'id'

# #     ReviewListCreateView,

# class UserList(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = ''

# class UserList(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

# class MeView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = 'id'
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         serializer = ProfileSerializer(request.user.profile)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
        
    return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({'token': token.key}, status=status.HTTP_200_OK)

