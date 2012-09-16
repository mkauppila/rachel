import socket

import parse

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

class UserInfo(object):
	""" Holds information about IRC user
	"""
	def __init__(self, nick, mode):
		self.nick = nick
		self.mode = mode

	def __str__(self):
		return mode + nick


class IRCClient(object):
	""" Handles communication with a IRC server.
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
		""" Send command to IRC server.

		Method adds the terminator characters 
		'\r\n' to the command before sending it.

		Args:
			command: String containing valid IRC command
			    without separator characters.
		"""
		self.logger.debug('send command: %s', command)

		command = command + '\r\n'
		self.connection.send(command)

	def get_messages(self):
		""" Receive messages from the server.

		The method receives data from the server through
		the connection and parses it into Message
		objects.

		Returns:
			List of parsed Message objects or None if there's
			network problems.
		"""
		data = self.connection.recv(4096)
		if not data:
			return None

		messages = []
		raw_messages = parse.parse_messages_from(data)
		for raw_message in raw_messages:
			message = parse.parse_message(raw_message)
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

	def send_names_to_channel(self, channel_name):
		command = 'NAMES %s' % channel_name
		self.send_command_to_server(command)

	def send_irc_message(self, channel, message):
		self.logger.debug('send irc message to channel %s', channel)
		command = 'PRIVMSG #%s :%s' % (channel, message)
		self.send_command_to_server(command)

	def send_set_mode(self, channel_name, nick, mode):
		command = "MODE #%s %s %s" % (channel_name, mode, nick)
		self.send_command_to_server(command)

	# Send response commands

	def send_pong_with_response(self, original_message):
		response = original_message.trailing
		command = 'PONG %s' % response
		self.send_command_to_server(command)
