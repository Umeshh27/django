from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Project, Issue, Comment
from .forms import IssueForm, CommentForm


def is_htmx_request(request):
    """
    Detect whether the incoming request is an enhanced HTMX/JS request.
    Inspects HTTP headers for HX-Request.
    """
    return (
        request.headers.get('HX-Request') == 'true' or
        request.META.get('HTTP_HX_REQUEST') == 'true' or
        request.headers.get('hx-request') == 'true'
    )


def project_list(request):
    """Display a list of all projects."""
    projects = Project.objects.all()
    return render(request, 'tracker/project_list.html', {
        'projects': projects,
    })


def project_board(request, project_id):
    """
    Main issue board view for a single project.
    Renders a full HTML page grouping issues by status:
    'To Do', 'In Progress', and 'Done'.
    """
    project = get_object_or_404(Project, pk=project_id)
    issues = project.issues.all()
    
    todo_issues = issues.filter(status=Issue.STATUS_TODO)
    in_progress_issues = issues.filter(status=Issue.STATUS_IN_PROGRESS)
    done_issues = issues.filter(status=Issue.STATUS_DONE)
    
    form = IssueForm()
    
    return render(request, 'tracker/project_board.html', {
        'project': project,
        'todo_issues': todo_issues,
        'in_progress_issues': in_progress_issues,
        'done_issues': done_issues,
        'form': form,
    })


@csrf_exempt
@require_POST
def issue_create(request, project_id):
    """
    Handle creating a new issue for a project.
    Accepts application/x-www-form-urlencoded POST data.
    Standard flow: redirects (302) to /projects/{project_id}/.
    """
    project = get_object_or_404(Project, pk=project_id)
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    status = request.POST.get('status', Issue.STATUS_TODO).strip()

    if title:
        # Validate status choice
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if status not in valid_statuses:
            status = Issue.STATUS_TODO

        Issue.objects.create(
            project=project,
            title=title,
            description=description,
            status=status
        )

    return redirect('project_board', project_id=project.id)


def issue_detail(request, issue_id):
    """
    Detail view for a single issue, displaying its description,
    associated comments, and a comment form.
    """
    issue = get_object_or_404(Issue, pk=issue_id)
    comments = issue.comments.all()
    comment_form = CommentForm()

    return render(request, 'tracker/issue_detail.html', {
        'issue': issue,
        'comments': comments,
        'comment_form': comment_form,
    })


@csrf_exempt
@require_POST
def update_issue_status(request, issue_id):
    """
    Update an issue's status.
    Differentiates between standard requests and HTMX requests:
    - Standard request: updates status and redirects (302) to project board.
    - Enhanced request (HX-Request: true): updates status and returns (200)
      ONLY the HTML fragment for the updated issue card (no <html> or <body>).
    """
    issue = get_object_or_404(Issue, pk=issue_id)
    new_status = request.POST.get('status', '').strip()

    valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
    if new_status in valid_statuses:
        issue.status = new_status
        issue.save()

    if is_htmx_request(request):
        # Return only the partial fragment for the issue card
        return render(request, 'tracker/_issue_card.html', {
            'issue': issue
        }, status=200)
    
    # Standard flow: redirect to the project board
    return redirect('project_board', project_id=issue.project.id)


@csrf_exempt
@require_POST
def add_comment(request, issue_id):
    """
    Add a comment to an issue.
    Differentiates between standard requests and HTMX requests:
    - Standard request: creates comment and redirects (302) to issue detail.
    - Enhanced request (HX-Request: true): creates comment and returns (200)
      ONLY the HTML fragment for the new comment (no <html> or <body>).
    """
    issue = get_object_or_404(Issue, pk=issue_id)
    content = request.POST.get('content', '').strip()

    comment = None
    if content:
        comment = Comment.objects.create(issue=issue, content=content)

    if is_htmx_request(request):
        if comment:
            return render(request, 'tracker/_comment.html', {
                'comment': comment
            }, status=200)
        # Empty comment submission fallback partial or empty response
        return render(request, 'tracker/_comment.html', {
            'comment': None
        }, status=200)

    # Standard flow: redirect to the issue detail page
    return redirect('issue_detail', issue_id=issue.id)
