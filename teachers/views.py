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
from django.db.models import Avg
from django.db.models import Sum, F, FloatField
from django.db.models.functions import Cast


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
        career = get_object_or_404(Career, id=serializer.validated_data["career_id"])

        profile.career = career
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
            for subject in career.subjects.all()
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
        enrollments = Enrollment.objects.filter(
            student=request.user.profile
        )

        total_credits = enrollments.filter(
            subject__credits__isnull=False
            ).aggregate(
                total_credits = Sum('subject__credits')
            )['total_credits'] or 0
        
        credits_completed = enrollments.filter(
                grade__isnull=False,
                subject__credits__isnull=False
            ).aggregate(
                total_credits=Sum("subject__credits"),
            )['total_credits'] or 0

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

        stats = {
            "gpa": gpa,

            "total_enrollments": enrollments.count(),

            "completed_enrollments": enrollments.filter(
                status=Enrollment.Status.COMPLETED
            ).count(),

            "total_reviews": enrollments.filter(
                review__isnull=False,
            ).count(),

            "total_credits": total_credits,

            "credits_completed": credits_completed,

            "credits_left": total_credits - credits_completed,

            "completion_rate": credits_completed / total_credits if total_credits > 0 and credits_completed > 0 else 0,
        }

        serializer = ProfileStatsSerializer(stats)
        return Response(serializer.data)

class TeacherListView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all().prefetch_related('enrollments__review', 'subjects', 'department')
    serializer_class = TeacherSerializer
    lookup_field = 'uuid'

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all().prefetch_related('enrollments__review', 'subjects', 'department')
    serializer_class = TeacherDetailSerializer
    lookup_field = 'uuid'

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

