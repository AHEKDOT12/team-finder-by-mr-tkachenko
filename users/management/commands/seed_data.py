from django.core.management.base import BaseCommand

from projects.models import Favorite, Project
from users.models import Skill, User


class Command(BaseCommand):
    help = "Create demo users, skills, projects, participants and favorites."

    def handle(self, *args, **options):
        skills_names = [
            "Python",
            "Django",
            "JavaScript",
            "React",
            "PostgreSQL",
            "Docker",
            "UI/UX",
            "HTML",
            "CSS",
        ]

        skills = {}
        for name in skills_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills[name] = skill

        users_data = [
            {
                "email": "maria@yandex.ru",
                "name": "Мария",
                "surname": "Иванова",
                "password": "password",
                "about": "Backend-разработчик. Люблю Django и аккуратную архитектуру.",
                "phone": "+79990000001",
                "github_url": "https://github.com/maria",
                "skills": ["Python", "Django", "PostgreSQL"],
            },
            {
                "email": "alex@example.com",
                "name": "Алексей",
                "surname": "Петров",
                "password": "password",
                "about": "Frontend-разработчик. Ищу интересные pet-проекты.",
                "phone": "+79990000002",
                "github_url": "https://github.com/alex",
                "skills": ["JavaScript", "React", "HTML", "CSS"],
            },
            {
                "email": "olga@example.com",
                "name": "Ольга",
                "surname": "Смирнова",
                "password": "password",
                "about": "Дизайнер интерфейсов, люблю понятные продукты.",
                "phone": "+79990000003",
                "github_url": "https://github.com/olga",
                "skills": ["UI/UX", "HTML", "CSS"],
            },
        ]

        users = {}

        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "about": data["about"],
                    "phone": data["phone"],
                    "github_url": data["github_url"],
                    "is_active": True,
                },
            )

            if created:
                user.set_password(data["password"])
                user.save()

            user.skills.set([skills[name] for name in data["skills"]])
            users[data["email"]] = user

        projects_data = [
            {
                "name": "TaskFlow",
                "description": "Сервис для командного планирования задач и отслеживания прогресса.",
                "owner": users["maria@yandex.ru"],
                "github_url": "https://github.com/maria/taskflow",
                "status": Project.STATUS_OPEN,
                "participants": [users["alex@example.com"]],
            },
            {
                "name": "DesignHub",
                "description": "Платформа для совместной работы дизайнеров и разработчиков над макетами.",
                "owner": users["olga@example.com"],
                "github_url": "https://github.com/olga/designhub",
                "status": Project.STATUS_OPEN,
                "participants": [users["maria@yandex.ru"]],
            },
            {
                "name": "DeployMate",
                "description": "Инструмент для простого деплоя pet-проектов через Docker.",
                "owner": users["alex@example.com"],
                "github_url": "https://github.com/alex/deploymate",
                "status": Project.STATUS_CLOSED,
                "participants": [users["maria@yandex.ru"], users["olga@example.com"]],
            },
        ]

        for data in projects_data:
            project, _ = Project.objects.get_or_create(
                name=data["name"],
                owner=data["owner"],
                defaults={
                    "description": data["description"],
                    "github_url": data["github_url"],
                    "status": data["status"],
                },
            )

            project.participants.add(data["owner"])
            project.participants.add(*data["participants"])

        Favorite.objects.get_or_create(
            user=users["maria@yandex.ru"],
            project=Project.objects.get(name="DesignHub"),
        )

        Favorite.objects.get_or_create(
            user=users["alex@example.com"],
            project=Project.objects.get(name="TaskFlow"),
        )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))