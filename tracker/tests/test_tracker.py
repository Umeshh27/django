from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection
from tracker.models import Project, Issue, Comment


class ProgressiveEnhancementTrackerTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test project
        self.project = Project.objects.create(
            id=1,
            name="Alpha Platform Core",
            description="Core e-commerce backend platform"
        )
        # Create initial issues
        self.todo_issue = Issue.objects.create(
            project=self.project,
            title="Design landing page wireframe",
            description="Create Figma mocks for the new portal",
            status="To Do"
        )
        self.in_progress_issue = Issue.objects.create(
            project=self.project,
            title="Implement database migrations",
            description="Run Django migrations for schema",
            status="In Progress"
        )
        self.done_issue = Issue.objects.create(
            project=self.project,
            title="Configure Docker Compose",
            description="Multi-container Docker setup",
            status="Done"
        )

    def test_database_schema_tables_and_columns(self):
        """Contract 2: Verify PostgreSQL/ORM schema for tracker_project, tracker_issue, tracker_comment."""
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
            self.assertIn('tracker_project', tables)
            self.assertIn('tracker_issue', tables)
            self.assertIn('tracker_comment', tables)

    def test_project_board_ssr(self):
        """Contract 3: GET /projects/{project_id}/ returns 200, full HTML document, issues grouped by status."""
        response = self.client.get(f'/projects/{self.project.id}/')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        # Full HTML document check
        self.assertIn('<html', content.lower())
        self.assertIn('<body', content.lower())
        self.assertIn('</html>', content.lower())
        self.assertIn('</body>', content.lower())

        # Status headings presence
        self.assertIn('To Do', content)
        self.assertIn('In Progress', content)
        self.assertIn('Done', content)

        # Issue titles presence under board
        self.assertIn(self.todo_issue.title, content)
        self.assertIn(self.in_progress_issue.title, content)
        self.assertIn(self.done_issue.title, content)

    def test_create_issue_standard(self):
        """Contract 4: POST /projects/{project_id}/issues/create/ standard form submission."""
        initial_count = Issue.objects.filter(project=self.project).count()

        payload = {
            'title': 'New Feature: Automated Backups',
            'description': 'Schedule daily backups to object storage',
            'status': 'To Do'
        }
        response = self.client.post(f'/projects/{self.project.id}/issues/create/', payload)
        
        # Must return 302 redirect to the project board
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/projects/{self.project.id}/')

        # Database state verification
        self.assertEqual(Issue.objects.filter(project=self.project).count(), initial_count + 1)
        created_issue = Issue.objects.get(title='New Feature: Automated Backups')
        self.assertEqual(created_issue.status, 'To Do')
        self.assertEqual(created_issue.project, self.project)

    def test_update_status_standard(self):
        """Contract 5: POST /issues/{issue_id}/update-status/ standard request with redirect."""
        self.assertEqual(self.todo_issue.status, 'To Do')

        response = self.client.post(
            f'/issues/{self.todo_issue.id}/update-status/',
            {'status': 'In Progress'}
        )

        # Must return 302 redirect back to the project board
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/projects/{self.project.id}/')

        # Verify database state
        self.todo_issue.refresh_from_db()
        self.assertEqual(self.todo_issue.status, 'In Progress')

    def test_add_comment_standard(self):
        """Contract 6: POST /issues/{issue_id}/comments/add/ standard request with redirect."""
        initial_comment_count = self.todo_issue.comments.count()

        response = self.client.post(
            f'/issues/{self.todo_issue.id}/comments/add/',
            {'content': 'This is a standard SSR comment.'}
        )

        # Must return 302 redirect back to issue detail page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/issues/{self.todo_issue.id}/')

        # Verify database state
        self.assertEqual(self.todo_issue.comments.count(), initial_comment_count + 1)
        new_comment = self.todo_issue.comments.last()
        self.assertEqual(new_comment.content, 'This is a standard SSR comment.')

    def test_update_status_htmx(self):
        """Contract 7 & 10: Progressively enhanced issue status update with HX-Request header."""
        self.assertEqual(self.todo_issue.status, 'To Do')

        response = self.client.post(
            f'/issues/{self.todo_issue.id}/update-status/',
            {'status': 'Done'},
            HTTP_HX_REQUEST='true'  # Simulate an HTMX request
        )

        # Response must be 200 OK
        self.assertEqual(response.status_code, 200)

        # Response must NOT contain full page HTML tags
        content = response.content.decode('utf-8')
        self.assertNotIn('<html>', content)
        self.assertNotIn('<body>', content)
        self.assertNotIn('<html', content.lower())
        self.assertNotIn('<!doctype', content.lower())

        # Response must contain the updated issue card HTML fragment
        self.assertIn(f'id="issue-{self.todo_issue.id}"', content)
        self.assertIn('Done', content)

        # Database state must be updated
        self.todo_issue.refresh_from_db()
        self.assertEqual(self.todo_issue.status, 'Done')

    def test_add_comment_htmx(self):
        """Contract 8 & 10: Progressively enhanced comment addition with HX-Request header."""
        initial_comment_count = self.todo_issue.comments.count()

        response = self.client.post(
            f'/issues/{self.todo_issue.id}/comments/add/',
            {'content': 'Enhanced real-time comment via HTMX!'},
            HTTP_HX_REQUEST='true'  # Simulate an HTMX request
        )

        # Response must be 200 OK
        self.assertEqual(response.status_code, 200)

        # Response must NOT contain full page HTML tags
        content = response.content.decode('utf-8')
        self.assertNotIn('<html>', content)
        self.assertNotIn('<body>', content)
        self.assertNotIn('<html', content.lower())

        # Response must contain comment fragment
        self.assertIn('Enhanced real-time comment via HTMX!', content)
        self.assertIn('comment-bubble', content)

        # Database state must be updated
        self.assertEqual(self.todo_issue.comments.count(), initial_comment_count + 1)

    def test_view_header_differentiation(self):
        """Contract 9: View correctly differentiates standard (302) vs enhanced (200 HTML fragment)."""
        # Request 1: No header -> 302 Redirect
        r1 = self.client.post(
            f'/issues/{self.todo_issue.id}/update-status/',
            {'status': 'In Progress'}
        )
        self.assertEqual(r1.status_code, 302)

        # Request 2: With HX-Request header -> 200 OK with partial HTML snippet
        r2 = self.client.post(
            f'/issues/{self.todo_issue.id}/update-status/',
            {'status': 'Done'},
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(r2.status_code, 200)
        self.assertNotIn('<html>', r2.content.decode('utf-8'))
