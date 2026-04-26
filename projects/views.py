from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Favorite, Project


PROJECTS_PER_PAGE = 12


def home_redirect(request):
    return redirect("projects:project_list")


def paginate_queryset(request, queryset, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def get_favorite_project_ids(user):
    if not user.is_authenticated:
        return set()

    return set(
        user.favorites.values_list(
            "project_id",
            flat=True,
        )
    )


def project_list(request):
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at", "-id")
    )

    page_obj = paginate_queryset(request, projects)

    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "favorite_project_ids": get_favorite_project_ids(request.user),
    }
    return render(request, "projects/project_list.html", context)


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants",
            "favorites",
        ),
        pk=project_id,
    )

    is_owner = request.user.is_authenticated and project.owner == request.user
    is_participant = (
        request.user.is_authenticated
        and project.participants.filter(pk=request.user.pk).exists()
    )
    is_favorite = (
        request.user.is_authenticated
        and project.favorites.filter(user=request.user).exists()
    )

    context = {
        "project": project,
        "is_owner": is_owner,
        "is_participant": is_participant,
        "is_favorite": is_favorite,
        "participants": project.participants.all(),
        "participants_count": project.participants.count(),
    }
    return render(request, "projects/project-details.html", context)


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:project_detail", project_id=project.pk)

    context = {
        "form": form,
        "is_edit": False,
    }
    return render(request, "projects/create-project.html", context)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return redirect("projects:project_detail", project_id=project.pk)

    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        project = form.save()
        return redirect("projects:project_detail", project_id=project.pk)

    context = {
        "form": form,
        "is_edit": True,
        "project": project,
    }
    return render(request, "projects/create-project.html", context)


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse(
            {"status": "error", "message": "Недостаточно прав."},
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже закрыт."},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {
            "status": "ok",
            "project_status": Project.STATUS_CLOSED,
        }
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.owner == request.user:
        return JsonResponse(
            {
                "status": "error",
                "message": "Автор уже является участником проекта.",
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        is_participant = False
    else:
        if project.status == Project.STATUS_CLOSED:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Нельзя присоединиться к закрытому проекту.",
                },
                status=HTTPStatus.BAD_REQUEST,
            )

        project.participants.add(request.user)
        is_participant = True

    return JsonResponse(
        {
            "status": "ok",
            "is_participant": is_participant,
            "participants_count": project.participants.count(),
        }
    )


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    favorite, created = request.user.favorites.get_or_create(
        project=project,
    )

    if created:
        is_favorite = True
    else:
        favorite.delete()
        is_favorite = False

    return JsonResponse(
        {
            "status": "ok",
            "is_favorite": is_favorite,
            "project_id": project.id,
        }
    )


@login_required
def favorite_projects(request):
    favorites = (
        request.user.favorites.select_related(
            "project",
            "project__owner",
        )
        .prefetch_related("project__participants")
        .order_by("-created_at", "-id")
    )

    page_obj = paginate_queryset(request, favorites)

    context = {
        "favorites": page_obj,
        "page_obj": page_obj,
        "favorite_project_ids": get_favorite_project_ids(request.user),
    }
    return render(request, "projects/favorites.html", context)