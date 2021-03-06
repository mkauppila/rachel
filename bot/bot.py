#! /usr/bin/python

import sys
import signal
import logging
import optparse

import irc
import parse
import config

# users eligible for ops
op_list = ['_markus']
# users eligible for voice
voice_list = []
# Users currently on the channel
users = {}

class DiscussionLog(object):
	""" DiscussionLog handles logging the IRC discussion.

	Decided to write DiscussionLog class since implementing the
	IRC discussion logging using Python's default logging module
	felt inelegant. Particularly using critical logging level
	for chat logging and the fact the changing logging level might
	have disabled the logging otherwise.
	"""

	def __init__(self, log_filename, buffer_size=1):
		""" Creates instance of DiscussionLog

		Args:
			log_filename: Name of the log file. The logger will log the 
				discussion in this file. If the file doesn't exists,
				it will be created. Otherwise, it'll be appended.
			buffer_size: Buffer size for the log file. By default the
				access is line buffered.
		"""
		self.log_file = open(log_filename, 'a', buffer_size)

	def close(self):
		""" Closes the log file
		"""
		self.log_file.close()

	def log(self, message, user=None):
		""" Write the message by nick to the log file

		If user is None, only the message is logged. 

		Args:
			message: IRC chat message that'll be logged
			user: who said message as User object.
				Defaults to None.
		"""
		if user:
			line = '<%s> %s\n' % (user, message)
		else:
			line = '%s\n' % (message)
		self.log_file.write(line)


# FIXM(mk): rename to set_up_debug_logging
def set_up_file_logger(filename):
	""" Sets up the logging facilities

	Sets up the handlers for the root logger. The 
	settings will cascade to all the child loggers
	"""
	# Get the root logger	
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	handler = logging.FileHandler(filename, mode='w')
	formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	handler.close()


def handle_bot_mode_change(mode):
	""" Handles mode changes for the bot

	Args:
		mode: 'v' or 'o' depending which one is bot's new mode
	"""
	if mode == 'v':
		client.send_irc_message(channel_name, "I got voice :( I need ops!")
	elif mode == 'o':
		client.send_irc_message(channel_name, "Yay, I got ops!")
		try_to_set_channel_modes()
	else:
		logger.debug('handle_bot_mode_change: unrecognized mode %s', mode)

	logger.debug('Handle bot mode change: %s', mode)


def try_to_set_channel_modes():
	""" Try to set the channel modes.

	"""
	if config.should_set_channel_mode == False:
		return 

	client.send_set_channel_mode_to(channel_name, config.channel_mode)
	logger.debug('set channel mode: %s', config.channel_mode)


def handle_names(message):
	""" Adds users of the channel based on NAMES list

	Args:
		message: Message object representing the original
		    message received from the server.
	"""
	channel_name = message.parameters.pop()
	logger.debug('names channel name: %s', channel_name)

	full_nicks = message.trailing.split(' ')
	for full_nick in full_nicks:
		nick, mode = parse.parse_nick(full_nick)

		if nick == config.bots_name:
			handle_bot_mode_change(mode)

		if users.has_key(nick):
			users[nick].mode = mode
		else:
			users[nick] = irc.UserInfo(nick, mode)

	# Try this, it'll fail if the bot doesn't have ops
	try_to_set_channel_modes()

def handle_join(message):
	""" Handles joining users

	Args:
		message: Message object representing the original
		    message received from the server.
	"""
	nick = parse.parse_nick_from_prefix(message.prefix)
	logger.debug("nick joined: '%s'", nick)

	# Skip over if the bot itself joins
	if nick == config.bots_name:
		return 

	mode = None
	if nick in op_list:
		mode = 'o'
		client.send_set_mode_for_user(channel_name, nick, "+o")
	elif nick in voice_list:
		mode = 'v'
		client.send_set_mode_for_user(channel_name, nick, "+v")

	users[nick] = irc.UserInfo(nick, mode)
	client.send_irc_message(channel_name, 'Hello %s' % nick)


def handle_part(message):
	""" Handles parting users

	Args:
		message: Message object representing the original
		    message received from the server.
	"""
	nick = parse.parse_nick_from_prefix(message.prefix)
	logger.debug("nick parted: %s", nick)
	if users.has_key(nick):
		del users[nick]
		logger.debug('removed "%s" from the users list' % nick)


def handle_irc_messages(message):
	""" Handle chat messages 

	The bot will do different tricks based on what is said 
	to it or on the channel where it is idling..

	Args:
		message: Message object representing the original
		    message received from the server.
	"""
	trailing = message.trailing
	message_sender = parse.parse_nick_from_prefix(message.prefix)


	# Log the message
	user = users[message_sender]
	channel_logger.log(trailing, user)


	# Process the message
	highlighted_name = "%s:" % config.bots_name
	# Did I get direct message?
	got_direct_message = trailing.find(highlighted_name) == 0
	if got_direct_message:
		# parse the actual message
		start_index = trailing.find(':') + 1
		message = trailing[start_index:].strip(' ')
		logger.debug("direct message: '%s'", message)

		# parse message.split(' ') -> 

		if message == '!op':
			if message_sender in op_list:
				client.send_set_mode_for_user(channel_name, message_sender, "+o")
			else:
				client.send_irc_message(channel_name, "Sorry, can't op you")

		# parse the trailing further and do something
	elif trailing.find(config.bots_name) > 0:
		# if trailing == VERSION, just skip
		# skip all not coming from right channel?
		# Eliza style?
		client.send_irc_message(channel_name, "Hey! Don't talk about me!")
	

def handle_nick_collision(message):
	""" Handles nick collision.

	If bot's primary nick is in use, add underline
	at the end and try again. This will keep adding
	underlines under nick is unique.

	If nick collision happens, the bot can't join
	the channel. So send join request again

	Args:
		message: IRC server message as Message object
	"""
	nick_already_in_use = message.parameters.pop()
	new_nick = nick_already_in_use + '_'
	client.send_nick(new_nick)
	client.send_join_channel(config.channel_name)
	# Update the global config
	config.bots_name = new_nick

def handle_mode(message):
	""" Changes mode for the users.

		Args:
		message: IRC server message as Message object
	"""
	if len(message.parameters) < 2:
		return 

	nick = message.parameters.pop()
	full_mode = message.parameters.pop()
	# full_mode is either +o or +v, we need only need the letter
	mode = full_mode[1] 

	logger.debug('%s received mode %s', nick, full_mode)

	# verify that mode is correct
	if mode in ['o', 'v']:
		global users
		user = users[nick]
		user.mode = mode

		if nick == config.bots_name:
			handle_bot_mode_change(mode)
	else:
		logger.debug("handle_mode: didn't recognize mode %s", mode)


def dispatch_message(dispatch_table, message):
	""" Dispatches the message to right handler function

	Args:
		dispatch_table: A dictionary containing handlers
			for messages. 
		message: IRC server message as Message object
	"""
	logger.debug('Handle message: %s', message)

	try:
		action = dispatch_table[message.command]
		action(message)
	except KeyError:
		pass 
	finally:
		# Just for debugging, disabled for real use
		if message.trailing:
			print message.trailing


if __name__ == '__main__':
	# Parse command line arguments
	version_string = 'bot version 0.1'
	option_parser = optparse.OptionParser(version=version_string)
	option_parser.add_option('-c', 
							 '--configuration-file',
							 action='store',
							 type='string',
							 dest='configuration_file',
							 help='select configuration file', 
							 metavar='example.conf')

	(options, args) = option_parser.parse_args()

	# set up signals
	def clean_up_on_exit(signal_number, frame):
		channel_logger.close()
		client.disconnect()
		sys.exit(0)

	signal.signal(signal.SIGINT,  clean_up_on_exit)
	signal.signal(signal.SIGTERM, clean_up_on_exit)

	# load configuration files
	configuration_file = config.default_configuration_file
	if options.configuration_file:
		configuration_file = options.configuration_file
	config.load_configuration_from(configuration_file)

	# setup up logging
	log_file = config.log_file_name
	set_up_file_logger(log_file)
	logger = logging.getLogger('main')

	# create irc client
	host = config.host
	port = config.port
	client_logger = logging.getLogger('IRCClient')
	client = irc.IRCClient(host, port, client_logger)
	client.send_nick(config.bots_name)
	client.send_user(config.bots_name, config.bots_real_name)

	channel_name = config.channel_name
	client.send_join_channel(channel_name)
	client.send_names_to_channel(channel_name)

	channel_logger = DiscussionLog('%s.irc' % channel_name)
	channel_logger.log('starts logging: %s' % channel_name)

	# defines what happens when certain message is received
	# from the IRC server
	# Apparently, local variables of this scope are also
	# accessible in functions added to dispatch_table 
	dispatch_table = {'PING' : client.send_pong_with_response,
				      'PRIVMSG' : handle_irc_messages,
				      'JOIN' : handle_join,
				      'PART' : handle_part,
				      'MODE' : handle_mode,
				      '353' : handle_names,
				      '433' : handle_nick_collision }
	while True:
		messages = client.get_messages()
		for message in messages:
			dispatch_message(dispatch_table, message)

	channel_logger.close()
	client.disconnect()