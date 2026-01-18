from django.contrib import admin
from .models import Teacher, Review, Department, Subject, Career, Profile, Enrollment
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.db.models.functions import Lower

class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = ('id', 'name', 'uuid', 'department_id')

class ReviewResource(resources.ModelResource):
    class Meta:
        model = Review
        fields = ('id', 'punctuality', 'clarity', 'justice', 'support', 'flexibility', 'knowledge', 'methodology', 'comment', 'created_at', 'updated_at', 'enrollment_id')

class DepartmentResource(resources.ModelResource):
    class Meta:
        model = Department
        fields = ('id', 'name')

class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'credits', 'period')


class CareeResource(resources.ModelResource):
    class Meta:
        model = Career
        fields = ('id', 'name', 'department_id')

class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        fields = ('id', 'career_id', 'user_id', 'onboarding_completed')


class EnrollmentResource(resources.ModelResource):
    class Meta:
        model = Enrollment
        fields = ('id', 'status', 'grade', 'student', 'teacher', 'completion_date', 'subject')



@admin.register(Teacher)
class TeacherAdmin(ImportExportModelAdmin):
    resource_classes = [TeacherResource]

    search_fields = ['name']
    list_display = ('id', 'name', 'uuid', 'department_id')

    def get_ordering(self, request):
        return [Lower('name')] 

@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    resource_classes = [ReviewResource]

    list_display = ('id', 'punctuality', 'clarity', 'justice', 'support', 'flexibility', 'knowledge', 'methodology', 'comment', 'created_at', 'updated_at', 'enrollment_id')


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_classes = [DepartmentResource]

    search_fields = ['name']
    list_display = ('id', 'name')


@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_classes = [SubjectResource]

    search_fields = ['name']
    list_display = ('id', 'name', 'credits', 'period')


@admin.register(Career)
class CareerAdmin(ImportExportModelAdmin):
    resource_classes = [CareeResource]

    search_fields = ['name']
    list_display = ('id', 'name', 'department')



@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    resource_classes = [ProfileResource]

    # prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ('id', 'career_id', 'user_id', 'onboarding_completed')

@admin.register(Enrollment)
class EnrollmentAdmin(ImportExportModelAdmin):
    resource_classes = [EnrollmentResource]

    search_fields = ('name', 'department')
    list_display = ('id', 'status', 'grade', 'student', 'teacher', 'completion_date', 'subject')
