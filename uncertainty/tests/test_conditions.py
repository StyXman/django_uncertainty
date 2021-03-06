from django.test import TestCase
from unittest.mock import MagicMock, patch

from uncertainty.conditions import (Predicate, NotPredicate, OrPredicate, AndPredicate,
                                    IsMethodPredicate, is_get, is_delete, is_post, is_put)


class PredicateTests(TestCase):
    def setUp(self):
        self.predicate = Predicate()
        self.other_predicate = MagicMock()

    def test_call_returns_true(self):
        """Test that invoking return True"""
        get_response_mock = MagicMock()
        request_mock = MagicMock()
        self.assertTrue(self.predicate(get_response_mock, request_mock))

    def test_negate_calls_not_predicate(self):
        """Test that negating the predicate calls NotPredicate"""
        with patch('uncertainty.conditions.NotPredicate') as not_predicate_mock:
            -self.predicate
            not_predicate_mock.assert_called_once_with(self.predicate)

    def test_negate_returns_not_predicate(self):
        """Test that negating the predicate returns a NotPredicate"""
        with patch('uncertainty.conditions.NotPredicate') as not_predicate_mock:
            self.assertEqual(not_predicate_mock.return_value, -self.predicate)

    def test_or_calls_or_predicate(self):
        """Test that using the bitwise or (|) operator with the predicate calls OrPredicate"""
        with patch('uncertainty.conditions.OrPredicate') as or_predicate_mock:
            self.predicate | self.other_predicate
            or_predicate_mock.assert_called_once_with(self.predicate, self.other_predicate)

    def test_or_returns_or_predicate(self):
        """Test that using the bitwise or (|) operator with the predicate a NotPredicate"""
        with patch('uncertainty.conditions.OrPredicate') as or_predicate_mock:
            self.assertEqual(or_predicate_mock.return_value, self.predicate | self.other_predicate)

    def test_and_calls_and_predicate(self):
        """Test that using the bitwise and (&) operator with the predicate calls OrPredicate"""
        with patch('uncertainty.conditions.AndPredicate') as and_predicate_mock:
            self.predicate & self.other_predicate
            and_predicate_mock.assert_called_once_with(self.predicate, self.other_predicate)

    def test_and_returns_and_predicate(self):
        """Test that using the bitwise and (&) operator with the predicate a NotPredicate"""
        with patch('uncertainty.conditions.AndPredicate') as and_predicate_mock:
            self.assertEqual(and_predicate_mock.return_value, self.predicate & self.other_predicate)


class NotPredicateTests(TestCase):
    def setUp(self):
        self.some_predicate = MagicMock()
        self.not_predicate = NotPredicate(self.some_predicate)
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_calls_encapsulated_predicate(self):
        """Tests that calling the NotPredicate calls the encapsulated predicate"""
        self.not_predicate(self.get_response_mock, self.request_mock)
        self.some_predicate.assert_called_once_with(self.get_response_mock, self.request_mock)

    def test_returns_false_when_encapsulated_predicate_returns_true(self):
        """Tests that calling the NotPredicate returns False when the encapsulated predicate
        returns True"""
        self.some_predicate.return_value = True
        self.assertFalse(self.not_predicate(self.get_response_mock, self.request_mock))

    def test_returns_true_when_encapsulated_predicate_returns_false(self):
        """Tests that calling the NotPredicate returns True when the encapsulated predicate
        returns False"""
        self.some_predicate.return_value = False
        self.assertTrue(self.not_predicate(self.get_response_mock, self.request_mock))


class OrPredicateTests(TestCase):
    def setUp(self):
        self.some_left_predicate = MagicMock()
        self.some_right_predicate = MagicMock()
        self.or_predicate = OrPredicate(self.some_left_predicate, self.some_right_predicate)
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_calls_left_encapsulated_predicate(self):
        """Tests that calling the OrPredicate calls the left encapsulated predicate"""
        self.or_predicate(self.get_response_mock, self.request_mock)
        self.some_left_predicate.assert_called_once_with(self.get_response_mock, self.request_mock)

    def test_doesnt_call_right_encapsulated_predicate_if_left_is_true(self):
        """Tests that calling the OrPredicate doesn't call the right encapsulated predicate if
        calling the left predicate returns True"""
        self.some_left_predicate.return_value = True
        self.or_predicate(self.get_response_mock, self.request_mock)
        self.some_right_predicate.assert_not_called()

    def test_calls_right_encapsulated_predicate_if_left_is_false(self):
        """Tests that calling the OrPredicate calls the right encapsulated predicate if
        calling the left predicate returns False"""
        self.some_left_predicate.return_value = False
        self.or_predicate(self.get_response_mock, self.request_mock)
        self.some_left_predicate.assert_called_once_with(self.get_response_mock, self.request_mock)

    def test_returns_true_if_left_encapsulated_predicate_is_true(self):
        """Tests that calling the OrPredicate returns True if calling the left encapsulated
        predicate is True"""
        self.some_left_predicate.return_value = True
        self.assertTrue(self.or_predicate(self.get_response_mock, self.request_mock))

    def test_returns_true_if_right_encapsulated_predicate_is_true(self):
        """Tests that calling the OrPredicate returns True if calling the right encapsulated
        predicate is True"""
        self.some_right_predicate.return_value = True
        self.assertTrue(self.or_predicate(self.get_response_mock, self.request_mock))

    def test_returns_false_if_encapsulated_predicates_are_false(self):
        """Tests that calling the OrPredicate returns False if calling both encapsulated predicates
        return False"""
        self.some_left_predicate.return_value = False
        self.some_right_predicate.return_value = False
        self.assertFalse(self.or_predicate(self.get_response_mock, self.request_mock))


class AndPredicateTests(TestCase):
    def setUp(self):
        self.some_left_predicate = MagicMock()
        self.some_right_predicate = MagicMock()
        self.and_predicate = AndPredicate(self.some_left_predicate, self.some_right_predicate)
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_calls_left_encapsulated_predicate(self):
        """Tests that calling the AndPredicate calls the left encapsulated predicate"""
        self.and_predicate(self.get_response_mock, self.request_mock)
        self.some_left_predicate.assert_called_once_with(self.get_response_mock,
                                                         self.request_mock)

    def test_doesnt_call_right_encapsulated_predicate_if_left_is_false(self):
        """Tests that calling the AndPredicate doesn't call the right encapsulated predicate if
        calling the left predicate returns False"""
        self.some_left_predicate.return_value = False
        self.and_predicate(self.get_response_mock, self.request_mock)
        self.some_right_predicate.assert_not_called()

    def test_calls_right_encapsulated_predicate_if_left_is_true(self):
        """Tests that calling the AndPredicate calls the right encapsulated predicate if
        calling the left predicate returns False"""
        self.some_left_predicate.return_value = True
        self.and_predicate(self.get_response_mock, self.request_mock)
        self.some_left_predicate.assert_called_once_with(self.get_response_mock,
                                                         self.request_mock)

    def test_returns_false_if_left_encapsulated_predicate_is_false(self):
        """Tests that calling the AndPredicate returns False if calling the left encapsulated
        predicate is False"""
        self.some_left_predicate.return_value = False
        self.assertFalse(self.and_predicate(self.get_response_mock, self.request_mock))

    def test_returns_false_if_right_encapsulated_predicate_is_false(self):
        """Tests that calling the AndPredicate returns True if calling the right encapsulated
        predicate is True"""
        self.some_right_predicate.return_value = False
        self.assertFalse(self.and_predicate(self.get_response_mock, self.request_mock))

    def test_returns_true_if_encapsulated_predicates_are_true(self):
        """Tests that calling the AndPredicate returns True if calling both encapsulated predicates
        return True"""
        self.some_left_predicate.return_value = True
        self.some_right_predicate.return_value = True
        self.assertTrue(self.and_predicate(self.get_response_mock, self.request_mock))


class IsMethodPredicateTests(TestCase):
    def setUp(self):
        self.some_method = MagicMock()
        self.is_method_predicate = IsMethodPredicate(self.some_method)
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_returns_true_if_request_method_is_encapsulated_method(self):
        """Tests that calling IsMethodPredicate returns True if the request method is the same as
        the encapsulated method"""
        self.request_mock.method = self.some_method
        self.assertTrue(self.is_method_predicate(self.get_response_mock, self.request_mock))

    def test_returns_false_if_request_method_is_nt_encapsulated_method(self):
        """Tests that calling IsMethodPredicate returns False if the request method is not the same
        as the encapsulated method"""
        self.request_mock.method = MagicMock()
        self.assertFalse(self.is_method_predicate(self.get_response_mock, self.request_mock))


class IsGetTests(TestCase):
    def setUp(self):
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_returns_true_if_request_method_is_get(self):
        """Tests that calling is_get returns True if the request method is 'GET'"""
        self.request_mock.method = 'GET'
        self.assertTrue(is_get(self.get_response_mock, self.request_mock))

    def test_returns_false_if_request_method_is_not_get(self):
        """Tests that calling is_get returns False if the request method is not 'GET'"""
        self.request_mock.method = 'FOOBAR'
        self.assertFalse(is_get(self.get_response_mock, self.request_mock))


class IsDeleteTests(TestCase):
    def setUp(self):
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_returns_true_if_request_method_is_delete(self):
        """Tests that calling is_delete returns True if the request method is 'DELETE'"""
        self.request_mock.method = 'DELETE'
        self.assertTrue(is_delete(self.get_response_mock, self.request_mock))

    def test_returns_false_if_request_method_is_not_delete(self):
        """Tests that calling is_delete returns False if the request method is not 'DELETE'"""
        self.request_mock.method = 'FOOBAR'
        self.assertFalse(is_delete(self.get_response_mock, self.request_mock))


class IsPostTests(TestCase):
    def setUp(self):
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_returns_true_if_request_method_is_post(self):
        """Tests that calling is_post returns True if the request method is 'POST'"""
        self.request_mock.method = 'POST'
        self.assertTrue(is_post(self.get_response_mock, self.request_mock))

    def test_returns_false_if_request_method_is_not_post(self):
        """Tests that calling is_post returns False if the request method is not 'POST'"""
        self.request_mock.method = 'FOOBAR'
        self.assertFalse(is_post(self.get_response_mock, self.request_mock))


class IsPutTests(TestCase):
    def setUp(self):
        self.get_response_mock = MagicMock()
        self.request_mock = MagicMock()

    def test_returns_true_if_request_method_is_post(self):
        """Tests that calling is_put returns True if the request method is 'PUT'"""
        self.request_mock.method = 'PUT'
        self.assertTrue(is_put(self.get_response_mock, self.request_mock))

    def test_returns_false_if_request_method_is_not_post(self):
        """Tests that calling is_put returns False if the request method is not 'PUT'"""
        self.request_mock.method = 'FOOBAR'
        self.assertFalse(is_put(self.get_response_mock, self.request_mock))


# TODO Add HasRequestParameterPredicate tests
# TODO Add PathMatchesRegexpPredicate tests
# TODO Add IsAuthenticatedPredicate tests
# TODO Add IsUserPredicate tests
