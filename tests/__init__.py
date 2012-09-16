import unittest

import test_parse

def make_suite():
	test_suites = []
	test_suites.append(test_parse.make_suite())

	suite = unittest.TestSuite(test_suites)
	return suite
