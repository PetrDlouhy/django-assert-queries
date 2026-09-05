"""Unit tests for template information in query results.

Version Added:
    3.0
"""

from __future__ import annotations

from django.template.loader import render_to_string
from django.test.testcases import TestCase

from django_assert_queries.query_catcher import catch_queries
from django_assert_queries.testing import assert_queries
from django_assert_queries.tests.models import TestModel


class TemplateInfoTests(TestCase):
    """Unit tests for template information in query results."""

    def test_query_in_template(self) -> None:
        """Testing catch_queries records the template nodes leading to a
        query
        """
        with catch_queries() as ctx:
            render_to_string('child.html')

        executed_queries = ctx.executed_queries
        self.assertEqual(len(executed_queries), 1)
        self.assertEqual(executed_queries[0]['template_info'], [
            {
                'template': 'child.html',
                'lineno': 1,
                'contents': 'extends "base.html"',
            },
            {
                'template': 'base.html',
                'lineno': 3,
                'contents': 'block content',
            },
            {
                'template': 'child.html',
                'lineno': 4,
                'contents': 'count_test_models',
            },
        ])

    def test_query_outside_template(self) -> None:
        """Testing catch_queries records no template nodes for a query made
        outside of template rendering
        """
        with catch_queries() as ctx:
            TestModel.objects.count()

        executed_queries = ctx.executed_queries
        self.assertEqual(len(executed_queries), 1)
        self.assertEqual(executed_queries[0]['template_info'], [])

    def test_assert_queries_with_template_info(self) -> None:
        """Testing assert_queries with with_template_info=True"""
        with self.assertRaises(AssertionError) as cm:
            with assert_queries([{'model': TestModel, 'limit': 1}],
                                with_template_info=True):
                render_to_string('child.html')

        self.assertIn(
            'From template:\n'
            '  child.html:1:\n'
            '    extends "base.html"\n'
            '  base.html:3:\n'
            '    block content\n'
            '  child.html:4:\n'
            '    count_test_models',
            str(cm.exception))

    def test_assert_queries_without_template_info(self) -> None:
        """Testing assert_queries with with_template_info=False"""
        with self.assertRaises(AssertionError) as cm:
            with assert_queries([{'model': TestModel, 'limit': 1}]):
                render_to_string('child.html')

        self.assertNotIn('From template:', str(cm.exception))
