
import unittest

import helpers

class TestHelper(unittest.TestCase):
	""" Test parsing server messages.

	Test that all the parts of server messages can be parsed properly.
	Doesn't include negative tests that ought to fail.
	"""
	
	def test_parse_full_message(self):
		prefix = 'zelazny.freenode.net'
		command = '372'
		parameters = ['booby']
		trailing = ':- Thank you for using freenode!'
		server_message = ':%s %s %s %s' % (prefix, command, ''.join(parameters), trailing)
		message = helpers.parse_message(server_message)

		self.assertEqual(message.prefix, prefix, 
			'prefixes should match. expected: "%s", got "%s"' % (message.prefix, prefix))
		self.assertEqual(message.command, command,
			'commands should match, expected "%s", got "%s"' % (command, message.command))		
		self.assertEqual(message.parameters, parameters,
			'parameters should match, expected "%s", got "%s"' % (parameters, message.parameters))
		self.assertEqual(message.trailing, trailing,
			'trailings should match, expected "%s", got "%s"' % (trailing, message.trailing))

	def test_parse_command_and_parameters(self):
		command = '353'
		parameters = ['booby', '@', '#markus_vs_warkus']
		trailing = ':- Thank you for using freenode!'
		server_message = '%s %s %s' % (command, ' '.join(parameters), trailing)
		message = helpers.parse_message(server_message)


		self.assertEqual(message.command, command,
			'commands should match, expected "%s", got "%s"' % (command, message.command))		
		self.assertEqual(message.parameters, parameters,
			'parameters should match, expected "%s", got "%s"' % (parameters, message.parameters))
		self.assertEqual(message.trailing, trailing,
			'trailings should match, expected "%s", got "%s"' % (trailing, message.trailing))

	def test_parse_all_but_trailing(self):
		prefix = 'zelazny.freenode.net'
		command = '353'
		parameters = ['booby', '@', '#markus_vs_warkus']
		server_message = ':%s %s %s' % (prefix, command, ' '.join(parameters))
		message = helpers.parse_message(server_message)


		self.assertEqual(message.prefix, prefix, 
			'prefixes should match. expected: "%s", got "%s"' % (message.prefix, prefix))
		self.assertEqual(message.command, command,
			'commands should match, expected "%s", got "%s"' % (command, message.command))		
		self.assertEqual(message.parameters, parameters,
			'parameters should match, expected "%s", got "%s"' % (parameters, message.parameters))

	def test_parse_all_but_prefix(self):
		command = '366'
		parameters = ['booby', '#markus_vs_warkus']
		trailing = ':End of /NAMES list.'
		server_message = '%s %s %s' % (command, ' '.join(parameters), trailing)
		message = helpers.parse_message(server_message)

		self.assertEqual(message.command, command,
			'commands should match, expected "%s", got "%s"' % (command, message.command))		
		self.assertEqual(message.parameters, parameters,
			'parameters should match, expected "%s", got "%s"' % (parameters, message.parameters))
		self.assertEqual(message.trailing, trailing,
			'trailings should match, expected "%s", got "%s"' % (trailing, message.trailing))

	def test_parse_command_and_trailing(self):
		command = 'PING'
		trailing = ':zelazny.freenode.net'
		server_message = '%s %s' % (command, trailing)
		message = helpers.parse_message(server_message)

		self.assertEqual(message.command, command,
			'commands should match, expected "%s", got "%s"' % (command, message.command))		
		self.assertEqual(message.trailing, trailing,
			'trailings should match, expected "%s", got "%s"' % (trailing, message.trailing))

	def test_parse_non_existant_message(self):
		message = helpers.parse_message('')
		self.assertEqual(message, None, "Message should be None")

		message = helpers.parse_message(None)
		self.assertEqual(message, None, "Message should be None")


def make_suite():
	return unittest.makeSuite(TestHelper, 'test')
