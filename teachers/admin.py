from django.contrib import admin
from .models import Teacher, Review, Department, Subject, Career, Profile, Enrollment
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class SubjectResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'credits', 'period')
        # export_order = ('id', 'name', 'credits')


class TeacherResource(resources.ModelResource):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'department')


@admin.register(Subject)
class SubjectAdmin(ImportExportModelAdmin):
    resource_classes = [SubjectResource]

    # prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ('name', 'credits', 'period')

    # @admin.display(description='Pre-Req')
    # def get_prereq_key(self, obj):
    #     return obj.prereq.key if obj.prereq else '-'


@admin.register(Teacher)
class SubjectAdmin(ImportExportModelAdmin):
    resource_classes = [SubjectResource]

    # prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'department')
    list_display = ('name', 'department')


admin.site.register(Review)
admin.site.register(Department)
admin.site.register(Career)
admin.site.register(Profile)
admin.site.register(Enrollment)