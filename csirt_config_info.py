import configparser

def get_value_from_config(config_file, section, variable_name):
    # Create a configparser object
    config = configparser.ConfigParser()

    # Read the config file
    config.read(config_file)

    # Check if the specified section exists in the config file
    if section not in config:
        raise ValueError(f"The section '{section}' does not exist in the config file.")

    # Check if the specified variable exists in the section
    if variable_name not in config[section]:
        raise ValueError(f"The variable '{variable_name}' does not exist in the '{section}' section.")

    # Retrieve the value of the variable
    return config[section][variable_name]


def get_openai_config():
    return get_value_from_config('config/config.ini', 'OPENAI', 'OPENAI_API_KEY')


def get_salesforce_config():
    config_file = 'config/config.ini'
    sf_config = {
        "sf_user": get_value_from_config(config_file, 'SALESFORCE', 'SF_USER'),
        "sf_passwd": get_value_from_config(config_file, 'SALESFORCE', 'SF_PASSWD'),
        "sf_client_id": get_value_from_config(config_file, 'SALESFORCE', 'SF_CLIENT_ID'),
        "sf_client_secret": get_value_from_config(config_file, 'SALESFORCE', 'SF_CLIENT_SECRET'),
    }
    return sf_config

def get_postgresql_config():
    config_file = 'config/config.ini'
    postgre_config = {
        "postgre_user": get_value_from_config(config_file, 'POSTGRE', 'POSTGRE_USER'),
        "postgre_passwd": get_value_from_config(config_file, 'POSTGRE', 'POSTGRE_PASSWD'),
        "postgre_host": get_value_from_config(config_file, 'POSTGRE', 'POSTGRE_HOST'),
        "postgre_database": get_value_from_config(config_file, 'POSTGRE', 'POSTGRE_DATABASE'),
        "postgre_port": get_value_from_config(config_file, 'POSTGRE', 'POSTGRE_PORT')
    }
    return postgre_config