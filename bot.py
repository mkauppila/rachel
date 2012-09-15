# !/bin/sh

import socket
import string

class Message(object):
	""" Represents the parsed irc message that's received from the server """
	def __init__(self, prefix, command, parameters, trailing):
		self.prefix = prefix
		self.command = command
		self.parameters = parameters
		self.trailing = trailing

HOST = 'irc.freenode.com'
PORT = 6667

timeout = None # seconds
address = (HOST, PORT)
connection = socket.create_connection(address, timeout)

data = connection.recv(4096)
print data

# helpers
# parse_message(message) -> return dict/tuple of the message

# client API

#client = IRCClient(host, port)

#client.send_default_nick()
#client.send_default_user()

#client.send_nick(nick) # used when nick changes
#client.send_user(nick, real_name)

#client.send_pong()
#client.send_join_channel(channel_name)

#client.receive_message() -> returns the message unparsed (shlfd)
#client.parsed_message() -> returns struct

#TODO(mk): handle command (handles the commands returned by the server)

connection.send('NICK booby\r\n')
connection.send('USER booby 0 * : Botty Bot\r\n')

connection.send('JOIN #markus_vs_warkus\r\n')

def parse_messages_from(data):
	""" Separates to irc server messages from the data """
	return data.split('\r\n')

def parse_message(message):
	# format is:
	# [:prefix] command [[param1] param2] [:trailing]
	# returns the data as struct
	if not message or message == '':
		return None

	prefix, command, params, trailing = None, None, None, None

	#print "-- debug: original message '%s'" % message

	# parse prefix
	if message[0] == ':':
		end_index = string.find(message, ' ')
		prefix = message[1:end_index]
		# remove the parsed section of the message and the whitespace
		message = message[end_index + 1:]
	
	#print "-- debug: prefix  message '%s'" % message

	# parse trailing
	start_index_of_trailing = string.find(message, ':')
	if start_index_of_trailing != -1: # has trailing
		trailing = message[start_index_of_trailing:]
		# update the message, only command and params left
		message = message[0:start_index_of_trailing]

	#print "-- debug: trailing message '%s'" % message

	command_and_params = message.split(' ')
	command = command_and_params[0]
	params = command_and_params[1:]

	"""
	print "-- debug: prefix: '%s'" % prefix
	print "-- debug: command: '%s'" % command
	print "-- debug: params: '%s'" % params
	print "-- debug: trailing: '%s'" % trailing
	"""

	return Message(prefix, command, params, trailing)

while True:
	data = connection.recv(4096)
	if not data:
		print "connection failed..."
		break

	# parse the data
	messages = parse_messages_from(data)
	for raw_message in messages:
		#print "full %s" % message
		message = parse_message(raw_message)
		if message and message.trailing:
			print message.trailing

		#print message_parts[2]
		#good_parts = parse_message(message)[2:]
		#print ' '.join(good_parts)

connection.close()
