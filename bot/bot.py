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
client.send_join_channel('markus_vs_warkus')

def handle_message(message):
	logger.debug('Handle message: %s', message)

	# TODO(mk): handle direct messages (trailing :booby: blaa)
	# TODO(mk): find bots name from the discussion and 
	#			make it responds to them. Eliza style?

	if message.command:
		if message.command == 'PING':
			client.send_pong_with_response(message.trailing)

	if message.trailing:
		print message.trailing

while True:
	messages = client.get_messages()
	for message in messages:
		handle_message(message)


client.disconnect()
