"""Unit tests for query shift detection functions."""

from django.test import TestCase

from django_assert_queries.query_comparator import (
    _basic_query_match,
    _detect_query_shift,
    _adjust_queries_for_shift,
    _queries_match_with_skip,
)


class QueryShiftDetectionTests(TestCase):
    """Unit tests for query shift detection functionality."""

    def setUp(self):
        """Set up mock objects for testing."""
        class MockQuery:
            def __init__(self, model, alias_map=None, alias_refcount=None):
                self.model = model
                self.alias_map = alias_map or {}
                self.alias_refcount = alias_refcount or {}

        class MockModel:
            class _meta:
                db_table = 'auth_user'

        class MockType:
            def __init__(self, value):
                self.value = value

        self.MockQuery = MockQuery
        self.MockModel = MockModel
        self.MockType = MockType

    def test_basic_query_match(self):
        """Test basic query matching logic."""
        expected_query = {
            'model': self.MockModel,
            'type': 'SELECT',
            'tables': {'auth_user'}
        }

        executed_query_info = {
            'query': self.MockQuery(self.MockModel),
            'type': self.MockType('SELECT')
        }

        # Test basic matching
        result = _basic_query_match(expected_query, executed_query_info)
        self.assertTrue(result)

        # Test with different type
        executed_query_info['type'].value = 'INSERT'
        result = _basic_query_match(expected_query, executed_query_info)
        self.assertFalse(result)

    def test_shift_detection_insertion(self):
        """Test detection of query insertion."""
        expected_queries = [
            {'model': self.MockModel, 'type': 'SELECT'},
            {'model': self.MockModel, 'type': 'SELECT'},
            {'model': self.MockModel, 'type': 'SELECT'}
        ]

        # Simulate an insertion at position 1
        executed_queries = [
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('INSERT')},  # Inserted
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
        ]

        shift_type, shift_pos = _detect_query_shift(expected_queries, executed_queries)
        self.assertEqual(shift_type, 'insertion')
        self.assertEqual(shift_pos, 1)

    def test_adjust_queries_for_insertion(self):
        """Test query adjustment for insertion shifts."""
        expected_queries = [
            {'model': self.MockModel, 'type': 'SELECT'},
            {'model': self.MockModel, 'type': 'SELECT'},
            {'model': self.MockModel, 'type': 'SELECT'}
        ]

        executed_queries = [
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('INSERT')},
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
            {'query': self.MockQuery(self.MockModel), 'type': self.MockType('SELECT')},
        ]

        adjusted, mapping = _adjust_queries_for_shift(
            expected_queries, executed_queries, 'insertion', 1
        )

        expected_mapping = [(0, 0), (-1, 1), (1, 2), (2, 3)]
        self.assertEqual(mapping, expected_mapping)
