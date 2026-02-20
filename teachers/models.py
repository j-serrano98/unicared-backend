import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Q



class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    career = models.ForeignKey('Career', on_delete=models.SET_NULL, null=True, blank=True, related_name="profiles")
    onboarding_completed = models.BooleanField(default=False)
    birthdate = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=25, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    linkedin_url = models.CharField(max_length=255, blank=True, null=True)
    fb_url = models.CharField(max_length=255, blank=True, null=True)
    github_user = models.CharField(max_length=100, blank=True, null=True)
    instagram_user = models.CharField(max_length=100, blank=True, null=True)

    def get_completion_rate(self):
        """Calculates rate using the 'enrollments' related_name."""
        stats = self.enrollments.aggregate(
            total=Sum('subject__credits'),
            completed=Sum('subject__credits', filter=Q(grade__isnull=False))
        )
        total = stats['total'] or 0
        completed = stats['completed'] or 0
        return completed / total if total > 0 else 0

    @property
    def current_rank(self):
        """Finds the tier based on the calculated rate."""
        rate = self.get_completion_rate()
        
        # Priority 1: Career-specific ranks
        rank = RankTier.objects.filter(
            career=self.career, 
            min_rate__lte=rate
        ).order_by('-min_rate').first()

        # Priority 2: Global/Default ranks
        if not rank:
            rank = RankTier.objects.filter(
                career__isnull=True, 
                min_rate__lte=rate
            ).order_by('-min_rate').first()
            
        return rank

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
        ordering = ['id']

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

    punctuality = models.PositiveSmallIntegerField(null=True, blank=True)
    clarity = models.PositiveSmallIntegerField(null=True, blank=True)
    justice = models.PositiveSmallIntegerField(null=True, blank=True)
    support = models.PositiveSmallIntegerField(null=True, blank=True)
    flexibility = models.PositiveSmallIntegerField(null=True, blank=True)
    knowledge = models.PositiveSmallIntegerField(null=True, blank=True)
    methodology = models.PositiveSmallIntegerField(null=True, blank=True)

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

        values = [v for v in fields if v is not None]

        if not values:
            return None

        return round(sum(values) / len(values), 2)
    
    # def __str__(self):
    #     return self.review.id
    
class RankTier(models.Model):
    career = models.ForeignKey(
        'Career', 
        on_delete=models.CASCADE, 
        related_name="ranks",
        help_text="The career this rank set belongs to. Leave null for a 'Default' set."
    )
    level_name = models.CharField(max_length=100)
    min_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="The minimum completion rate required for this rank (0.0 to 1.0)"
    )
    color_code = models.CharField(max_length=20, default="slate", help_text="Tailwind color name")

    class Meta:
        ordering = ['min_rate']
        unique_together = ('career', 'min_rate')

    def __str__(self):
        return f"[{self.career.name}] {self.level_name} (>= {self.min_rate})"















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

