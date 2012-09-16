#! /usr/bin/python

import logging

import irc
import parse

import config

config.load_configuration_from('bot.conf')

HOST = config.host
PORT = config.port
LOG_FILE = config.log_file_name

op_list = []
voice_list = ['_markus']

def set_up_logger():
	""" Sets up the logging facilities

	Sets up the handlers for the root logger. The 
	settings will cascade to all the child loggers
	"""
	# Get the root logger	
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	handler = logging.FileHandler(LOG_FILE, mode='w')
	formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	handler.close()

set_up_logger()

logger = logging.getLogger('main')

client_logger = logging.getLogger('IRCClient')
client = irc.IRCClient(HOST, PORT, client_logger)
client.send_default_nick()
client.send_default_user()

channel_name = 'markus_vs_warkus'
client.send_join_channel(channel_name)
client.send_names_to_channel(channel_name)

users = {}

def handle_names(message):
	""" Adds users of the channel based on NAMES list
	"""
	channel_name = message.parameters.pop()
	logger.debug('names channel name: %s', channel_name)

	full_nicks = message.trailing.split(' ')
	for full_nick in full_nicks:
		nick, mode = parse.parse_nick(full_nick)


		if users.has_key(nick):
			users[nick].mode = mode
		else:
			users[nick] = irc.UserInfo(nick, mode)

def handle_join(message):
	nick = parse.parse_nick_from_prefix(message.prefix)
	logger.debug("nick joined: %s", nick)

	# Skip over if the bot itself joins
	if nick == 'booby':
		return 

	# check if the nick is eligible for +v or +o
	#	set the rights to mode variable
	mode = None

	if nick in op_list:
		mode = 'o'
		client.send_set_mode(channel_name, nick, "+o")
	if nick in voice_list:
		mode = 'v'
		client.send_set_mode(channel_name, nick, "+v")

	users[nick] = irc.UserInfo(nick, mode)
	client.send_irc_message(channel_name, 'Hello %s' % nick)

def handle_part(message):
	nick = parse_nick_from_prefix(message.prefix)
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
	# Did I get direct message?
	got_direct_message = trailing.find('booby:') == 0
	if got_direct_message:
		client.send_irc_message(channel_name, "I'm not talking to you!")

		# parse the trailing further and do something
	elif trailing.find('booby') > 0:
		# if trailing == VERSION, just skip
		# skip all not coming from right channel?
		# Eliza style?
		client.send_irc_message(channel_name, "Hey! Don't talk about me!")
	else:
		# they're just talking...
		pass



def dispatch_message(message):
	""" Dispatches the message to right handler function

	Args:
		message: IRC server message as Message object
	"""
	logger.debug('Handle message: %s', message)

	actions = {'PING' : client.send_pong_with_response,
			   'PRIVMSG' : handle_irc_messages,
			   'JOIN' : handle_join,
			   'PART' : handle_part,
			   '353' : handle_names }

	try:
		action = actions[message.command]
		action(message)
	except KeyError:
		pass 
	finally:
		# Just for debugging, disabled for real use
		if message.trailing:
			print message.trailing

# The main loop 
while True:
	messages = client.get_messages()
	for message in messages:
		dispatch_message(message)

client.disconnect()
