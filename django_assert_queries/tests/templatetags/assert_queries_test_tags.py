"""Template tags used to test template information in query results.

Version Added:
    3.0
"""

from __future__ import annotations

from django import template

from django_assert_queries.tests.models import TestModel

register = template.Library()


@register.simple_tag
def count_test_models() -> int:
    """Run a query from within a template.

    Returns:
        int:
        The number of test models.
    """
    return TestModel.objects.count()
