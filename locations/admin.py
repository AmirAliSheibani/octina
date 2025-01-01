from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['latitude', 'longitude']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [field for field in fields if field != 'created_by']
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(created_by=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            user = request.user
            if not user.is_superuser:
                user_profile_count = models.Positions.objects.filter(created_by=user).count()
                user_limit = 10  # Set the desired limit here

                if user_profile_count >= user_limit:
                    raise ValidationError("You have reached the record creation limit.")

            obj.created_by = user

        super().save_model(request, obj, form, change)
