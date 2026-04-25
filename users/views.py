from http import HTTPStatus

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import LoginForm, ProfileEditForm, RegistrationForm
from .models import Skill, User


USERS_PER_PAGE = 12
SKILL_SUGGESTIONS_LIMIT = 10


def paginate_queryset(request, queryset, per_page=USERS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def user_list(request):
    active_skill = request.GET.get("skill")

    participants = (
        User.objects.prefetch_related("skills", "owned_projects")
        .order_by("-id")
    )

    if active_skill:
        participants = participants.filter(
            skills__name=active_skill,
        ).distinct()

    page_obj = paginate_queryset(request, participants)

    context = {
        "participants": page_obj,
        "page_obj": page_obj,
        "all_skills": Skill.objects.order_by("name"),
        "active_skill": active_skill,
    }
    return render(request, "users/participants.html", context)


def user_detail(request, user_id):
    profile_user = get_object_or_404(
        User.objects.prefetch_related("skills", "owned_projects"),
        pk=user_id,
    )

    context = {
        "user": profile_user,
        "projects": profile_user.owned_projects.all().order_by("-created_at", "-id"),
        "skills": profile_user.skills.all().order_by("name"),
        "is_owner": request.user.is_authenticated and request.user.pk == profile_user.pk,
    }
    return render(request, "users/user-details.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:project_list")

    form = RegistrationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("projects:project_list")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:project_list")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:project_list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


@login_required
def edit_profile(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:user_detail", user_id=request.user.pk)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    form = PasswordChangeForm(
        user=request.user,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:user_detail", user_id=request.user.pk)

    return render(request, "users/change_password.html", {"form": form})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()

    skills = Skill.objects.all()

    if query:
        skills = skills.filter(name__istartswith=query)

    skills = skills.order_by("name")[:SKILL_SUGGESTIONS_LIMIT]

    data = [
        {
            "id": skill.id,
            "name": skill.name,
        }
        for skill in skills
    ]

    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_user_skill(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)

    if request.user.pk != profile_user.pk:
        return JsonResponse(
            {"status": "error", "message": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN,
        )

    skill_id = request.POST.get("skill_id")
    name = request.POST.get("name", "").strip()

    if not skill_id and not name:
        return JsonResponse(
            {
                "status": "error",
                "message": "Передайте skill_id или name.",
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    created = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    else:
        skill, created = Skill.objects.get_or_create(name=name)

    already_has_skill = profile_user.skills.filter(pk=skill.pk).exists()

    if not already_has_skill:
        profile_user.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.id,
            "name": skill.name,
            "created": created,
            "added": not already_has_skill,
        }
    )


@login_required
@require_POST
def remove_user_skill(request, user_id, skill_id):
    profile_user = get_object_or_404(User, pk=user_id)

    if request.user.pk != profile_user.pk:
        return JsonResponse(
            {"status": "error", "message": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN,
        )

    skill = get_object_or_404(Skill, pk=skill_id)

    if not profile_user.skills.filter(pk=skill.pk).exists():
        return JsonResponse(
            {
                "status": "error",
                "message": "У пользователя нет такого навыка.",
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    profile_user.skills.remove(skill)

    return JsonResponse(
        {
            "status": "ok",
            "removed": True,
            "skill_id": skill.id,
        }
    )