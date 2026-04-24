from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^(\+7|8)\d{10}$",
    message="Введите телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX.",
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть email.")
        if not name:
            raise ValueError("У пользователя должно быть имя.")
        if not surname:
            raise ValueError("У пользователя должна быть фамилия.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя должен быть is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя должен быть is_superuser=True.")

        return self.create_user(email, name, surname, password, **extra_fields)


class Skill(models.Model):
    name = models.CharField(
        "Название навыка",
        max_length=124,
        unique=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Email",
        unique=True,
    )
    name = models.CharField(
        "Имя",
        max_length=124,
    )
    surname = models.CharField(
        "Фамилия",
        max_length=124,
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
    )
    phone = models.CharField(
        "Телефон",
        max_length=12,
        blank=True,
        validators=[phone_validator],
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    about = models.CharField(
        "О себе",
        max_length=256,
        blank=True,
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="users",
        blank=True,
        verbose_name="Навыки",
    )
    is_active = models.BooleanField(
        "Активен",
        default=True,
    )
    is_staff = models.BooleanField(
        "Администратор",
        default=False,
    )
    date_joined = models.DateTimeField(
        "Дата регистрации",
        default=timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ["-id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"