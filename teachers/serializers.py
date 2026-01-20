from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.db.models import Avg, F, FloatField

class ProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    career_name = serializers.ReadOnlyField(source='career.name')
    
    class Meta:
        model = Profile
        fields = ['user', 'username', 'email', 'first_name', 'last_name', 'career', 'career_name', 'onboarding_completed']

class SelectCareerSerializer(serializers.Serializer):
    career_id = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileStatsSerializer(serializers.Serializer):
    gpa = serializers.FloatField(allow_null=True)
    total_enrollments = serializers.IntegerField()
    completed_enrollments = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    total_credits = serializers.IntegerField()
    credits_completed = serializers.IntegerField()
    credits_left = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class ReviewSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    # skills = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id',
                  'updated_at',
                  'average',
                  'username',
                  'subject_name',
                  'comment',
                  'punctuality',
                  'clarity',
                  'justice',
                  'support',
                  'flexibility',
                  'knowledge',
                  'methodology']

    # def get_skills(self, obj):
    #     skills = {
    #         "Punctuality": obj.punctuality,
    #         "Clarity": obj.clarity,
    #         "Justice": obj.justice,
    #         "Support": obj.support,
    #         "Flexibility": obj.flexibility,
    #         "Knowledge": obj.knowledge,
    #         "Methodology": obj.methodology,
    #     }

    #     return [
    #         {"skill": skill, "score": score }
    #         for skill, score in skills.items()
    #     ]
    
# class CareerSerializer(serializers.ModelSerializer):
#     subject_name = serializers.ReadOnlyField(source='subject.name')
#     class Meta:
#         model = Career
#         fields = ['id', 'name', 'subject_name']

# class UserMeSerializer(serializers.ModelSerializer):
#     career = CareerSerializer(source="profile.career")

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'career']

class EnrollmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_credits = serializers.IntegerField(source="subject.credits", read_only=True)
    subject_period = serializers.IntegerField(source="subject.period", read_only=True)
    
    status = serializers.ChoiceField(
        choices=Enrollment.Status.choices,
        required=False
    )
    
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        allow_null=True,
        required=False,
    )

    teacher_name = serializers.CharField(
        source="teacher.name",
        read_only=True,
        default=None,
    )

    review = ReviewSerializer(required=False, allow_null=True)

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "subject",
            "subject_name",
            "subject_credits",
            "subject_period",
            "status",
            "grade",
            "teacher",
            "teacher_name",
            "review",
            "completion_date",
            "review",
        ]
    
    def get_status(self, obj):
        return obj.get_status_display()
    
    def update(self, instance, validated_data):
        review_data = validated_data.pop("review", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if review_data is not None:
            Review.objects.update_or_create(
                enrollment = instance,
                defaults=review_data
            )

        return instance
    

class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ['id', 'name', 'teachers', 'credits', 'period']


class TeacherSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    subjects = serializers.StringRelatedField(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    skill_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = ['uuid',
                  'name',
                  'department_name',
                  'rating',
                  'reviews_count',
                  'skill_rating',
                  'subjects',
                  ]

    def get_rating(self, obj):
        result = obj.enrollments.filter(
            review__isnull=False
        ).aggregate(
            rating=Avg(
                (
                    F('review__punctuality') +
                    F('review__clarity') +
                    F('review__justice') +
                    F('review__support') +
                    F('review__flexibility') +
                    F('review__knowledge') +
                    F('review__methodology') 
                ) / 7.0,
                output_field=FloatField()
            )
        )

        return result['rating']
    
    def get_skill_rating(self, obj):
        averages = obj.enrollments.filter(
            review__isnull=False
        ).aggregate(
            Punctuality=Avg('review__punctuality'),
            Clarity=Avg('review__clarity'),
            Justice=Avg('review__justice'),
            Support=Avg('review__support'),
            Flexibility=Avg('review__flexibility'),
            Knowledge=Avg('review__knowledge'),
            Methodology=Avg('review__methodology'),
        )

        return [
            {
                "skill": skill, 
                "score": round(score, 2) if score is not None else 0,
            }
            for skill, score in averages.items()
        ]

    def get_reviews_count(self, obj):
        return obj.enrollments.filter(
            review__isnull=False
        ).count()
    

class TeacherDetailSerializer(TeacherSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields + ['reviews']

    def to_representation(self, instance):

        representation = super().to_representation(instance)
        
        enrollments = instance.enrollments.filter(review__isnull=False)
        reviews = [e.review for e in enrollments]
        
        representation['reviews'] = ReviewSerializer(reviews, many=True).data
        return representation