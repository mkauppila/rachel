import ConfigParser

# default config file 
# note: this can't be overridden in configuration file
default_configuration_file = 'bot.conf'


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
    if config.has_section(section):
        host = get('host')
        port = get('port')
        channel_name = get('channel_name')
    else:
        print "configuration warning: %s is missing section %s" % (configuration_file, section)

    section = 'logging'
    if config.has_section(section):
        log_file_name = get('log_file_name') 
    else:
        print "configuration warning: %s is missing section %s" % (configuration_file, section)

    section = 'bot'
    if config.has_section(section):
        bots_name = get('name')
    else:
        print "configuration warning: %s is missing section %s" % (configuration_file, section)


def save_configuration_to(configuration_file):
	pass         
