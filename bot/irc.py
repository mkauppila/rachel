import socket

import helpers

class Message(object):
	""" Parsed server message.

	Represents parsed IRC server message. If optional part
	of message wasn't present in the parsed message, its
	value is None.
	""" 
	def __init__(self, prefix, command, parameters, trailing):
		self.prefix = prefix
		self.command = command
		self.parameters = parameters
		self.trailing = trailing

	def __str__(self):
		return "%s %s %s %s" % (self.prefix, self.command,
								self.parameters, self.trailing)


def add_command_terminator(command):
	""" Add terminator characters.

	Adds '\r\n' to the end of the command.

	Return:
		Properly terminated command, ready for sending
	"""
	return command + '\r\n';


class IRCClient(object):
	""" Handles communication with the IRC server
	"""

	def __init__(self, host, port, logger):
		self.host = host
		self.port = port
		self.logger = logger

		self.connection = None
		self.connect()

	def connect(self):
		# Close old connection, before making a new one
		if self.connection:
			self.connection.close()

		address = (self.host, self.port)
		timeout = None
		self.connection = socket.create_connection(address, timeout)
		self.logger.info('Connected to %s:%s', self.host, self.port)

	def disconnect(self):
		self.connection.close()
		sel.logger.info('Disconnected from %s', self.host)

	def send_command_to_server(self, command):
		self.logger.debug('send command: %s', command)
		command = add_command_terminator(command)
		self.connection.send(command)

	def get_messages(self):
		""" This is blocking method 
		Might block if there's no messages in the queue?

		Returns: (should be yield?)
			List of message objects 
			None if error happened and no message in queue
		"""
		data = self.connection.recv(4096)
		if not data:
			return None

		messages = []
		raw_messages = helpers.parse_messages_from(data)
		for raw_message in raw_messages:
			message = helpers.parse_message(raw_message)
			if message:
				messages.append(message)

		return messages

	# Send canned commands to the server

	def send_default_nick(self):
		command = 'NICK booby'
		self.send_command_to_server(command)
		
	def send_default_user(self):
		command = 'USER booby 0 * : Botty Bot'
		self.send_command_to_server(command)

	def send_join_channel(self, channel_name):
		command  = 'JOIN #%s' % channel_name
		self.send_command_to_server(command)
		
	#client.send_default_nick()
	#client.send_default_user()

	#client.send_nick(nick) # used when nick changes
	#client.send_user(nick, real_name)

	#client.send_pong()
	#client.send_join_channel(channel_name)

	#client.parsed_message() -> returns struct

