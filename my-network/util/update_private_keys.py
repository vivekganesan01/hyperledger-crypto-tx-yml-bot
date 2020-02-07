# Module helps to replace the CA private keys in yaml file
#   CA_PRIVATE_KEY is being used by the ca container which gets created at time of config tx MSP cert
#   generation.Each organization has its own ca private keys, this program will loop through the number
#   of organization specified in the config.ini and updates the ca private key in the yaml files. so
#   make sure config.ini is up to date.
#
# __author__ : vivek ganesan <vivekganesan01@gmail.com>
#
import configparser
import os


class PrivateKeyReplacer:
    """Replace CA private certs"""
    def __init__(self):
        print('################### CA PRIVATE KEY REPLACER #####################################')
        print(' * - reading config.ini')
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.start_up_sh = 'start-up.sh'

    @staticmethod
    def tokenizer(file, search, replace):
        """Helps search and replace within a given file.

        :param file: file name
        :param search: search string
        :param replace: place string
        :return: None
        """
        with open(file, 'r') as raw_file:
            contents = raw_file.read()
            contents = contents.replace(search, replace)
        with open(file, 'w') as new_file:
            new_file.write(contents)

    def ca_private_key_replacer(self):
        """Updates the CA private key for each organization in e2e yaml file.

        :return: None
        """
        print(' * - Replacing PRIVATE KEY for CA')
        _org_count = self.config['orderer']['Number_of_org']
        ca_private = {}
        for each_org in range(1, int(_org_count)+1):
            _org_header = 'org{}'.format(each_org)
            _org_name = self.config[_org_header]['Name']
            _domain = self.config['orderer']['Domain']
            _pk_path = '{}/crypto-config/peerOrganizations/{}.{}/ca'.format(os.getcwd(), _org_name, _domain)
            print(' * - {}'.format(_pk_path))
            if os.path.exists(_pk_path):
                for each_files in os.listdir(_pk_path):
                    if '_sk' in each_files:
                        ca_private['CA{}_PRIVATE_KEY'.format(each_org)] = each_files
            else:
                print('WARNING: CA private file doesn\'t exists {}'.format(_pk_path))
        for each_items in ca_private.keys():
            print(' * - updating : {}'.format(each_items))
            self.tokenizer('docker-compose-e2e.yaml', each_items, ca_private[each_items])
        print(' * - end')

    def update_start_up_var(self):
        print('########################## UPDATING STARTUP SH SCRIPT ENV VARIABLES  ################')
        print(' * - updating sys channel, channel, profile env to startup.sh files')
        self.tokenizer(self.start_up_sh, 'ORG_SYS_CHANNEL', self.config['channel']['ORG_SYS_CHANNEL_NAME'])
        self.tokenizer(self.start_up_sh, 'ORG_ORDERER_GENESIS_PROFILE', self.config['channel']['ORG_ORDERER_GENESIS_PROFILE'])
        self.tokenizer(self.start_up_sh, 'ORG_CHANNEL_NAME', self.config['channel']['ORG_CHANNEL_NAME'])
        self.tokenizer(self.start_up_sh, 'ORG_CHANNEL_PROFILE_NAME', self.config['channel']['ORG_CHANNEL_PROFILE'])
        _org_count = self.config['orderer']['Number_of_org']
        list_of_org = []
        for each_org in range(1, int(_org_count)+1):
            _org_header = 'org{}'.format(each_org)
            _org_name = self.config[_org_header]['Name']
            list_of_org.append(_org_name)
        shell_list_org = " ".join(list_of_org)
        self.tokenizer(self.start_up_sh, 'LIST_ORG_NAMES', '"{}"'.format(shell_list_org))
        print(' * - end.')


if __name__ == '__main__':
    pk = PrivateKeyReplacer()
    pk.ca_private_key_replacer()
    pk.update_start_up_var()
