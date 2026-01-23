import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    career = models.ForeignKey('Career', on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")
    onboarding_completed = models.BooleanField(default=False)
    birthdate = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    linkedin_url = models.CharField(max_length=255, blank=True, null=True)
    fb_url = models.CharField(max_length=255, blank=True, null=True)
    github_user = models.CharField(max_length=100, blank=True, null=True)
    instagram_user = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Teacher(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='teachers')
    
    class Meta:
        db_table = 'teachers'
        verbose_name = 'Teacher'

    def __str__(self):
        return self.name
    
class Department(models.Model):
    name = models.CharField(max_length=100)
    # code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'

    def __str__(self):
        return self.name
    
class Career(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField('Subject', blank=True, related_name='careers')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='careers')

    class Meta:
        db_table = 'careers'
        verbose_name = 'Career'

    def __str__(self):
        return self.name
    
class Subject(models.Model):
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField(Teacher, related_name='subjects', blank=True)
    # slug = models.SlugField(max_length=100, unique=True)
    # key = models.CharField(max_length=50, unique=True)
    credits = models.IntegerField(default=0)
    period = models.IntegerField(default=0)
    # prereq = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='prerequisites')

    class Meta:
        db_table = 'subjects'
        verbose_name = 'Subject'
        ordering = ['-id']

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    class Status(models.TextChoices):
        NOT_TAKEN = "NT", "Not taken"
        IN_PROGRESS = "IP", "In progress"
        COMPLETED = "CM", "Completed"

    student = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        related_name="enrollments",
        null=True
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments"
    )

    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NOT_TAKEN)
    grade = models.FloatField(null=True, blank=True)

    completion_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = "student", "subject"

    def __str__(self):
        return f"{self.student} - {self.subject}"

class Review(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="review", null=True, blank=True)

    punctuality = models.PositiveSmallIntegerField()
    clarity = models.PositiveSmallIntegerField()
    justice = models.PositiveSmallIntegerField()
    support = models.PositiveSmallIntegerField()
    flexibility = models.PositiveSmallIntegerField()
    knowledge = models.PositiveSmallIntegerField()
    methodology = models.PositiveSmallIntegerField()

    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        ordering = ['-created_at']
    
    @property
    def average(self):
        fields = [
            self.punctuality,
            self.clarity,
            self.justice,
            self.support,
            self.flexibility,
            self.knowledge,
            self.methodology
        ]
        return round((sum(fields) / len(fields)),2)
    
    # def __str__(self):
    #     return self.review.id
    


















# class Section(models.Model):
#     class Modality(models.TextChoices):
#         PRESENTIAL = 'PRES', 'Presencial'
#         VIRTUAL = 'VIRT', 'Virtual'

    # subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sections')
    # teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='sections')
#     name = models.CharField(max_length=10)
#     max_students = models.IntegerField()
#     modality = models.CharField(max_length=4, choices=Modality.choices, default=Modality.PRESENTIAL)

#     class Meta:
#         db_table = 'sections'
#         verbose_name = 'Section'
#         unique_together = ('subject', 'name')

#     def __str__(self):
#         return f"{self.subject.name} - Seccion {self.name}"

