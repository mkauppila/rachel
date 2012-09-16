#! /usr/bin/python

import logging

import irc

HOST = 'irc.freenode.com'
PORT = 6667
LOG_FILE = 'bot.log'

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

def parse_nick(nick):
	""" @_markus => (_markus, '@') 
	"""
	modes = ['@', 'v']
	if nick[0] in modes:
		return (nick[1:], nick)
	else:
		return (nick, None)

users = {}

def add_users(message):
	""" Adds users of the channel based on NAMES list """
	channel_name = message.parameters.pop()
	logger.debug('names channel name: %s', channel_name)

	full_nicks = message.trailing.split(' ')
	for full_nick in full_nicks:
		nick, mode = parse_nick(full_nick)

		users[nick] = irc.UserInfo(nick, mode)


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
	got_direct_message = trailing.find('booby') == 0
	if got_direct_message:
		logger.info('Somebody is talking to me!')
		# parse the trailing further and do something
	else:
		# if trailing == VERSION, just skip
		# skip all not coming from right channel?
		logger.info('Im a real person, not a bot!')
		# Eliza style?

actions = {'PING' : client.send_pong_with_response,
		   'PRIVMSG' : handle_irc_messages,
		   '353' : add_users }

def handle_message(message):
	logger.debug('Handle message: %s', message)

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
		handle_message(message)

client.disconnect()
