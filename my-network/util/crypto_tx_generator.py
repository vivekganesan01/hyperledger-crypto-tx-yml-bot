# Module helps to generate configtx.yaml and crypto-config.yaml
#   Creates tx configuration and crypto configuration based on the config.ini, so
#   make sure config.ini is up to date.
#
#   HFC version used: 1.4.3
#
# __author__ : vivek ganesan <vivekganesan01@gmail.com>
#
import configparser
import yaml
import os


class ConfigTx:
    """Creates ready to use configtx.yaml and crypto-config.yaml"""
    def __init__(self):
        print('################################### Start ##################################')
        self.config_tx = "configtx.yaml"
        self.crypto_config = "crypto-config.yaml"
        self.config = configparser.ConfigParser()
        print(' * - {}'.format(os.getcwd()))
        self.config.read('config.ini')
        self.config_transactions_list = []

    def organizations(self):
        """Updates organization information.

        :return: None
        """
        print('############################# ORG #########################################')
        __order_organization = ['# organization\n', 'Organizations:\n', '    - &OrdererOrg\n',
                                '        Name: {}Org\n'.format(self.config['orderer']['Name']),
                                '        ID: {}\n'.format(self.config['orderer']['MSPID']),
                                '        MSPDir: '
                                'crypto-config/ordererOrganizations/{}/msp\n'.format(self.config['orderer']['Domain']),
                                '        Policies:\n',
                                '            Readers:\n', '                Type: Signature\n',
                                '                Rule: "OR(\'OrdererMSP.member\')"\n',
                                '            Writers:\n', '                Type: Signature\n',
                                '                Rule: "OR(\'OrdererMSP.member\')"\n',
                                '            Admins:\n', '                Type: Signature\n',
                                '                Rule: "OR(\'OrdererMSP.admin\')"\n']
        self.config_transactions_list.extend(__order_organization)
        print(' * - number of org : {}'.format(self.config['orderer']['Number_of_org']))
        for org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            org_header = 'org{}'.format(org)
            org_id = '{}MSP'.format(self.config[org_header]['Name'])
            __orderer_org = ['    - &Org{}\n'.format(org),
                             '        Name: {}\n'.format(self.config[org_header]['Name']),
                             '        ID: {}\n'.format(org_id),
                             '        MSPDir: crypto-config/peerOrganizations/{}.{}/msp\n'.format(
                                 self.config[org_header]['Name'], self.config['orderer']['Domain']),
                             '        Policies:\n',
                             '            Readers:\n', '                Type: Signature\n',
                             '                Rule: "OR(\'{ID}.admin\', \'{ID}.peer\', \'{ID}.client\')"\n'.format(
                                 ID=org_id),
                             '            Writers:\n', '                Type: Signature\n',
                             '                Rule: "OR(\'{ID}.admin\', \'{ID}.client\')"\n'.format(ID=org_id),
                             '            Admins:\n', '                Type: Signature\n',
                             '                Rule: "OR(\'{ID}.admin\')"\n'.format(ID=org_id),
                             '        AnchorPeers:\n',
                             '            - Host: peer0.{}.{}\n'.format(self.config[org_header]['Name'],
                                                                        self.config['orderer']['Domain']),
                             '              Port: {}\n'.format(self.config[org_header]['Port'])]
            self.config_transactions_list.extend(__orderer_org)
            print(' * - updated orgMSP : {}'.format(org_id))

    def orderer(self):
        """Updates Orderer organization.

        :return: None
        """
        print('################################# ORDERER ##################################')
        print(' * - updating {}.{}:{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'],
                                       self.config['orderer']['Port']))
        __orderer = ['# orderer\n', 'Orderer: &OrdererDefaults\n',
                     '    OrdererType: solo\n',
                     '    Addresses:\n', '        - {}.{}:{}\n'.format(self.config['orderer']['HostName'],
                                                                       self.config['orderer']['Domain'],
                                                                       self.config['orderer']['Port']),
                     '    BatchTimeout: 2s\n',
                     '    BatchSize:\n',
                     '        MaxMessageCount: 10\n',
                     '        AbsoluteMaxBytes: 99 MB\n',
                     '        PreferredMaxBytes: 512 KB\n',
                     '    Organizations:\n', '    Policies:\n', '        Readers:\n',
                     '            Type: ImplicitMeta\n', '            Rule: "ANY Readers"\n',
                     '        Writers:\n', '            Type: ImplicitMeta\n',
                     '            Rule: "ANY Writers"\n',
                     '        Admins:\n', '            Type: ImplicitMeta\n',
                     '            Rule: "MAJORITY Admins"\n',
                     '        BlockValidation:\n', '            Type: ImplicitMeta\n',
                     '            Rule: "ANY Writers"\n', '\n']
        self.config_transactions_list.extend(__orderer)
        print(' * - updated orderer')

    # todo: Need to revisit, might not be needed.
    def capabilities(self):
        """Updated capabilities.

        :return: None
        """
        print('################################# CAPABILITY ##################################')
        __capability = ['# capabilities\n', 'Capabilities:\n', '    Channel: &ChannelCapabilities\n',
                        '        V1_4_3: true\n', '        V1_3: false\n', '        V1_1: false\n',
                        '    Orderer: &OrdererCapabilities\n', '        V1_4_2: true\n', '        V1_1: false\n',
                        '    Application: &ApplicationCapabilities\n', '        V1_4_2: true\n',
                        '        V1_3: false\n', '        V1_2: false\n', '        V1_1: false\n', '\n']
        self.config_transactions_list.extend(__capability)
        print(' * - done.')

    def applications(self):
        """Updates app level permissions/policies.

        :return: None
        """
        print('################################ APPLICATION ##################################')
        __application = ['# application\n', 'Application: &ApplicationDefaults\n', '    Organizations:\n',
                         '    Policies:\n',
                         '        Readers:\n', '            Type: ImplicitMeta\n', '            Rule: "ANY Readers"\n',
                         '        Writers:\n', '            Type: ImplicitMeta\n', '            Rule: "ANY Writers"\n',
                         '        Admins:\n', '            Type: ImplicitMeta\n',
                         '            Rule: "MAJORITY Admins"\n',
                         '    Capabilities:\n', '        <<: *ApplicationCapabilities\n', '\n']
        self.config_transactions_list.extend(__application)
        print(' * - done.')

    def channels(self):
        """Updates channel policies.

        :return: None
        """
        print('############################## CHANNEL POLICIES ################################')
        __channel = ['# channel\n', 'Channel: &ChannelDefaults\n', '    Policies:\n',
                     '        Readers:\n', '            Type: ImplicitMeta\n', '            Rule: "ANY Readers"\n',
                     '        Writers:\n', '            Type: ImplicitMeta\n', '            Rule: "ANY Writers"\n',
                     '        Admins:\n', '            Type: ImplicitMeta\n', '            Rule: "MAJORITY Admins"\n',
                     '    Capabilities:\n', '        <<: *ChannelCapabilities\n', '\n']
        self.config_transactions_list.extend(__channel)

    # todo: need to parametrize org channel name and genesis block name
    def profiles(self):
        """Creates the profile based on the policies and other configuration.

        :return: None
        """
        print('################################ PROFILES ##################################')
        main_profile = ['# Profile\n', 'Profiles:\n']
        org_list = []
        for org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            element = '                    - *Org{}\n'.format(org)
            org_list.append(element)
        __orderer_genesis = ['    {}:\n'.format(self.config['channel']['ORG_ORDERER_GENESIS_PROFILE']),
                             '        <<: *ChannelDefaults\n',
                             '        Orderer:\n',
                             '            <<: *OrdererDefaults\n',
                             '            Organizations:\n',
                             '                - *OrdererOrg\n',
                             '            Capabilities:\n',
                             '                <<: *OrdererCapabilities\n',
                             '        Consortiums:\n',
                             '            SampleConsortium:\n',
                             '                Organizations:\n']
        __orderer_genesis.extend(org_list)
        __org_channels = ['    {}:\n'.format(self.config['channel']['ORG_CHANNEL_PROFILE']),
                          '        Consortium: SampleConsortium\n',
                          '        <<: *ChannelDefaults\n', '        Application:\n',
                          '            <<: *ApplicationDefaults\n',
                          '            Organizations:\n']
        __org_channels.extend(org_list)
        __org_channels.extend(['            Capabilities:\n', '                <<: *ApplicationCapabilities\n'])
        print(' * - updating orderer genesis profile')
        main_profile.extend(__orderer_genesis)
        print(' * - updating channel profile')
        main_profile.extend(__org_channels)
        self.config_transactions_list.extend(main_profile)
        print(' * - end.')

    def generate_crypto_config(self):
        print('############################### CRYPTO CONFIG #################################')
        _output_stream = open(self.crypto_config, 'w')
        print(' * - updating orderer configuration')
        orderer = [
            {
                'Name': self.config['orderer']['Name'],
                'Domain': self.config['orderer']['Domain'],
                'Specs': [{
                    'HostName': self.config['orderer']['HostName'],
                }]
            }
        ]
        peers = []
        for org in range(1, int(self.config['orderer']['Number_of_org'])+1):
            print(' * - updating for org{}'.format(org))
            single_peer = {
                'Name': '{}'.format(self.config['org{}'.format(org)]['Name']),
                'Domain': '{}.{}'.format(self.config['org{}'.format(org)]['Name'], self.config['orderer']['Domain']),
                'EnableNodeOUs': False,
                'Template': {
                    'Count': int(self.config['org{}'.format(org)]['PeerCount']),
                },
                'Users': {
                    'Count': int(self.config['org{}'.format(org)]['Users']),
                }
            }
            peers.append(single_peer)
        crypto_dictionary = {
            "OrdererOrgs": orderer,
            "PeerOrgs": peers
        }
        yaml.dump(crypto_dictionary, _output_stream, default_flow_style=False)
        print(' * - end.')

    def run(self):
        self.generate_crypto_config()
        self.organizations()
        self.orderer()
        self.capabilities()
        self.applications()
        self.channels()
        self.profiles()
        file_output = open(self.config_tx, 'w')
        file_output.writelines(self.config_transactions_list)
        file_output.close()
        
        
if __name__ == '__main__':
    ctx = ConfigTx()
    ctx.run()
