import ConfigParser

# name of default configuration file
# note: this value can't be overriden by configuration file
default_configuration_file = 'bot.conf'

# Variables who's values can be overriden by configuraiton file
# They're set to their default values
bots_name = 'booby'
bots_real_name = 'Boobie bot'
host = 'irc.freenode.com'
port = '6667'
channel_name = 'markus_vs_warkus'
log_file_name = '%s.log' % bots_name

def print_missing_section_warning(missing_section):
    print ("Warning: Given configuration file is missing section '%s'"
            % (missing_section))
    print ("         Default values for the section will be used.")


def load_configuration_from(configuration_file):
    """ Load configuration file

    Loads the given configuration file and sets the variables
    in this module to the loaded values. If configuration file
    doesn't have required section, a warning will be printed
    and default values will be used.

    Args:
        configuration_file: Filename of the configuration file
            that will be loaded
    """
    config = ConfigParser.ConfigParser()
    config.read(configuration_file)

    # get access to config variables
    global host
    global port
    global channel_name
    global bots_name
    global log_file_name

    section = ''
    # Lambda simplifies loading the values from the sections
    # of the configuration file. It uses the current value
    # of section variable to access the right section in the
    # aforementioned file.
    get = lambda name: config.get(section, name) 

    section = 'general'
    if config.has_section(section):
        host = get('host')
        port = get('port')
        channel_name = get('channel_name')
    else:
        print_missing_section_warning(section)

    section = 'logging'
    if config.has_section(section):
        log_file_name = get('log_file_name') 
    else:
        print_missing_section_warning(section)

    section = 'bot'
    if config.has_section(section):
        bots_name = get('name')
        bots_real_name = get('real_name')
    else:
        print_missing_section_warning(section)


def save_configuration_to(configuration_file):
	pass         
