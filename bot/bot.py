#! /usr/bin/python

import irc

HOST = 'irc.freenode.com'
PORT = 6667

client = irc.IRCClient(HOST, PORT)
client.send_default_nick()
client.send_default_user()
client.send_join_channel('markus_vs_warkus')

def handle_message(message):
	if message.trailing:
		print message.trailing

while True:
	messages = client.get_messages()
	for message in messages:
		handle_message(message)

	#TODO(mk): handle command (handles the commands returned by the server)

client.disconnect()
