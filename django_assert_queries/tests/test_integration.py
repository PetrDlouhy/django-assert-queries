"""Integration tests for query shift detection functionality."""

from django.db.models import Q
from django.test import TestCase

from django_assert_queries import assert_queries
from django_assert_queries.tests.models import Author

class QueryShiftIntegrationTests(TestCase):
    """Integration tests for query shift detection functionality."""

    def test_normal_case(self):
        """Test that normal query matching still works."""
        author = Author.objects.create(name="Test Author")
        expected_queries = [{
            "model": Author, 
            "tables": {"tests_author"},
            "where": Q(pk=author.pk)
        }]
        
        with assert_queries(expected_queries):
            Author.objects.get(pk=author.pk)

    def test_shift_detection(self):
        """Test that query shifts are detected and reported helpfully."""
        author = Author.objects.create(name="Test Author")
        expected_queries = [{"model": Author, "tables": {"tests_author"}}]
        
        with self.assertRaises(AssertionError) as cm:
            with assert_queries(expected_queries):
                Author.objects.get(pk=author.pk)
                Author.objects.filter(name="nonexistent").exists()  # Extra query
        
        error_message = str(cm.exception)
        self.assertIn("Expected 1 queries, but got 2", error_message)
