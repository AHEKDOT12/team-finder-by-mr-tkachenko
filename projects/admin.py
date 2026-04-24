from django.contrib import admin

from .models import Favorite, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    ordering = ("-created_at", "-id")
    filter_horizontal = ("participants",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "user__email",
        "user__name",
        "user__surname",
        "project__name",
    )
    ordering = ("-created_at", "-id")