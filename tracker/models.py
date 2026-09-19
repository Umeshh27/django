from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'tracker_project'
        ordering = ['id']

    def __str__(self):
        return self.name


class Issue(models.Model):
    STATUS_TODO = 'To Do'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_DONE = 'Done'

    STATUS_CHOICES = [
        (STATUS_TODO, 'To Do'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_DONE, 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tracker_issue'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.title}"


class Comment(models.Model):
    content = models.TextField()
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tracker_comment'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment #{self.id} on Issue #{self.issue_id}"
