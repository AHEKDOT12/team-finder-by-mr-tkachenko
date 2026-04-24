from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыт"),
        (STATUS_CLOSED, "Закрыт"),
    ]

    name = models.CharField(
        "Название проекта",
        max_length=200,
    )
    description = models.TextField(
        "Описание",
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор проекта",
    )
    created_at = models.DateTimeField(
        "Дата создания",
        auto_now_add=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    status = models.CharField(
        "Статус",
        max_length=6,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Проект",
    )
    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_user_project_favorite",
            )
        ]
        ordering = ["-created_at", "-id"]
        verbose_name = "Избранный проект"
        verbose_name_plural = "Избранные проекты"

    def __str__(self):
        return f"{self.user} — {self.project}"