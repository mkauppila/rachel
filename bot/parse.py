import irc

def parse_nick(nick):
	""" Separates nick from the mode characters.

	Examples:
		parse_nick('@_markus') => (_markus, 'o')
		parse_nick('+_markus') => ('_markus', 'v')
	"""

	converter = {'@' : 'o', '+' : 'v'}

	modes = converter.keys()
	first_character = nick[0]
	if first_character in modes:
		return (nick[1:], converter[first_character])
	else:
		return (nick, None)

def parse_nick_from_prefix(prefix):
	""" Parse nick from the beginning of message prefix

	Used by JOIN and PART message handlers.
	"""
	end_index  = prefix.find('!')
	return prefix[0:end_index]

def parse_messages_from(data):
	""" Separate server messages 
	"""
	return data.split('\r\n')

def parse_message(message):
	""" Parse messages from IRC server.

	Message format is:
		[:prefix] command [[param1] param2] [:trailing]
	Only command is mandatory, other parts are optional.

	Args:
		Message: Server message that'll be parsed

	Returns:
		Message object containing the parsed information.

	"""
	if not message or message == '':
		return None

	prefix, command, params, trailing = None, None, None, None

	# parse prefix
	if message[0] == ':':
		end_index = message.find(' ')
		prefix = message[1:end_index]
		# remove the parsed section of the message and the whitespace
		message = message[end_index + 1:]
	
	# parse trailing
	start_index_of_trailing = message.find(':')
	if start_index_of_trailing != -1: # has trailing
		trailing = message[start_index_of_trailing + 1:]
		# update the message, only command and params left
		message = message[0:start_index_of_trailing]

	# remove redundant white space
	message = message.strip(' ')

	command_and_params = message.split(' ')
	command = command_and_params[0]
	params = command_and_params[1:]

	return irc.Message(prefix, command, params, trailing)
