import ConfigParser

bots_name = 'booby'
host = 'irc.freenode.com'
port = '6667'
channel_name = 'markus_vs_warkus'
log_file_name = '%s.log' % bots_name

def load_configuration_from(configuration_file):
    """
    """
    config = ConfigParser.ConfigParser()
    if not config:
        print "failed ot load configuration file"
    config.read(configuration_file)


    global host
    global port
    global channel_name
    global bots_name
    global log_file_name

    section = ''
    # Reads the section from the variable and uses it
    # reading information from the configuration file
    get = lambda name: config.get(section, name) 

    section = 'general'
    host = get('host')
    port = get('port')
    channel_name = get('channel_name')

    section = 'logging'
    log_file_name = get('log_file_name') 

    section = 'bot'
    bots_name = get('name')


def save_configuration_to(configuration_file):
	pass         
