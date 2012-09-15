import unittest

import test_helpers

def make_suite():
	test_suites = []
	test_suites.append(test_helpers.make_suite())

	suite = unittest.TestSuite(test_suites)
	return suite
