from django.core.management.base import BaseCommand
from tracker.models import Project, Issue, Comment


class Command(BaseCommand):
    help = 'Seeds the database with initial projects, issues, and comments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Checking database seed status...'))

        projects_data = [
            {
                'id': 1,
                'name': 'Alpha Platform Core',
                'description': 'Main web application and customer-facing portal architecture.',
                'issues': [
                    {
                        'title': 'Implement progressive enhancement for issue board',
                        'description': 'Ensure issue status changes work without JavaScript using standard form submissions.',
                        'status': 'Done',
                        'comments': [
                            'Initial SSR prototype built with Django views.',
                            'HTMX attributes layered on top for zero-refresh DOM swaps.'
                        ]
                    },
                    {
                        'title': 'Add multi-container Docker Compose configuration',
                        'description': 'Setup web and PostgreSQL database containers with health checks and persistence.',
                        'status': 'In Progress',
                        'comments': [
                            'PostgreSQL healthcheck configured with pg_isready.',
                            'Web service healthcheck configured with HTTP curl check.'
                        ]
                    },
                    {
                        'title': 'Integrate real-time notification badge',
                        'description': 'Show live badge counter when new comments or status updates occur.',
                        'status': 'To Do',
                        'comments': []
                    },
                    {
                        'title': 'Audit accessibility and keyboard navigation',
                        'description': 'Verify WCAG compliance across all board columns and modal forms.',
                        'status': 'To Do',
                        'comments': []
                    }
                ]
            },
            {
                'id': 2,
                'name': 'Mobile Companion App',
                'description': 'Cross-platform mobile client for field technicians and remote teams.',
                'issues': [
                    {
                        'title': 'Setup offline storage cache',
                        'description': 'Cache pending issue changes in local SQLite storage when network drops.',
                        'status': 'In Progress',
                        'comments': [
                            'Schema sync designed and evaluated.'
                        ]
                    },
                    {
                        'title': 'Push notifications for critical priority issues',
                        'description': 'Register FCM tokens and dispatch push notifications on assignments.',
                        'status': 'To Do',
                        'comments': []
                    },
                    {
                        'title': 'Biometric authentication integration',
                        'description': 'Allow FaceID and fingerprint unlock for quick login.',
                        'status': 'Done',
                        'comments': [
                            'Tested successfully on iOS and Android devices.'
                        ]
                    }
                ]
            },
            {
                'id': 3,
                'name': 'Cloud Infrastructure & SRE',
                'description': 'Kubernetes clusters, CI/CD pipelines, and observability monitoring.',
                'issues': [
                    {
                        'title': 'Automate database backup and point-in-time recovery',
                        'description': 'Nightly WAL-G backups to S3 bucket with lifecycle transition policies.',
                        'status': 'Done',
                        'comments': [
                            'Disaster recovery test completed successfully.'
                        ]
                    },
                    {
                        'title': 'Configure Prometheus alerts for slow database queries',
                        'description': 'Alert on queries taking longer than 250ms consistently.',
                        'status': 'To Do',
                        'comments': []
                    }
                ]
            }
        ]

        for p_data in projects_data:
            project, created = Project.objects.get_or_create(
                id=p_data['id'],
                defaults={
                    'name': p_data['name'],
                    'description': p_data['description'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created project: {project.name} (ID: {project.id})"))
            else:
                self.stdout.write(f"Project exists: {project.name} (ID: {project.id})")

            for i_data in p_data['issues']:
                issue, issue_created = Issue.objects.get_or_create(
                    project=project,
                    title=i_data['title'],
                    defaults={
                        'description': i_data['description'],
                        'status': i_data['status'],
                    }
                )
                if issue_created:
                    self.stdout.write(f"  - Created issue: {issue.title} [{issue.status}]")
                    for c_content in i_data.get('comments', []):
                        Comment.objects.create(issue=issue, content=c_content)
                else:
                    self.stdout.write(f"  - Issue exists: {issue.title}")

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))
