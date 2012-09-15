#! /usr/bin/python

import sys
import os
import unittest

# path needs to be updated before importing the tests
# package
project_path = os.path.abspath("bot") 
if project_path not in sys.path:
	sys.path.append(project_path)

import tests

if __name__ == '__main__':
	runner = unittest.TextTestRunner(verbosity=2)
	suite = tests.make_suite()
	runner.run(suite)
