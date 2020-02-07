#  Module:
#       Helps to auto-generate some of the docker composer yaml files for hfc.
#       Files include:
#           docker-compose-base.yaml
#           docker-compose-ca.yaml
#           docker-compose-e2e.yaml
#           docker-compose-couch.yaml
#       cli configuration is integrated as part of the docker-compose-e2e.yaml
#
#
# __author__ : vivek ganesan <vivekganesan01@gmail.com>
#
import configparser
import yaml


class DockerFiles:
    """The class represents hfc docker compose auto-generation.
    This helps to auto-generate all the hfc docker files, all the required input is fetched from
    config.ini file.
    """
    def __init__(self):
        print('#################### Docker compose yaml auto-generation ####################')
        self.docker_compose_base_file = 'docker-compose-base.yaml'
        self.docker_compose_base_peer = 'peer-base.yaml'
        self.docker_compose_ca_file = 'docker-compose-ca.yaml'
        self.docker_compose_e2e_file = 'docker-compose-e2e.yaml'
        self.docker_compose_couch_file = 'docker-compose-couch.yaml'
        print(' * - reading config.ini')
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

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

    def docker_composer_base(self):
        """Helps to generate base yaml.

        :return: None
        """
        print('#################### Generating docker base yaml ####################')
        _main_config = {
            'version': '2',
        }
        # orderer config
        print(' * - updating orderer services')
        _config = {}
        _orderer_host = '{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'])
        order = {
            'container_name': _orderer_host,
            'extends': {
                'file': '{}'.format(self.docker_compose_base_peer),
                'service': 'orderer-base',
            },
            'volumes': [
                '../channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block',
                '../crypto-config/ordererOrganizations/{}/orderers/{}/msp:'
                '/var/hyperledger/orderer/msp'.format(self.config['orderer']['Domain'], _orderer_host),
                '../crypto-config/ordererOrganizations/{}/orderers/{}/tls/:'
                '/var/hyperledger/orderer/tls'.format(self.config['orderer']['Domain'], _orderer_host),
                '{}:/var/hyperledger/production/orderer'.format(_orderer_host)
            ],
            'ports': ['"{port}:{port}"'.format(port=self.config['orderer']['Port'])]
        }
        _config[_orderer_host] = order
        print(' * - updating peer services')
        for each_org in range(1, int(self.config['orderer']['Number_of_org'])+1):
            _org_header = 'org{}'.format(each_org)
            _org_name = self.config[_org_header]['Name']
            _domain = self.config['orderer']['Domain']
            _peer_count = int(self.config['org{}'.format(each_org)]['PeerCount'])
            for each_peer in range(0, _peer_count):
                _peer_host = 'peer{}.{}.{}'.format(each_peer, _org_name, _domain)
                # gossip peer # Todo: revisit
                gossip_peer = 0 if each_peer != 0 else 1
                peer = {
                    'container_name': _peer_host,
                    'extends': {
                        'file': '{}'.format(self.docker_compose_base_peer),
                        'service': 'peer-base',
                    },
                    'environment': [
                        'CORE_PEER_ID={}'.format(_peer_host),
                        'CORE_PEER_ADDRESS={}:{}'.format(_peer_host, self.config[_org_header]['Port']),
                        'CORE_PEER_LISTENADDRESS=0.0.0.0:{}'.format(self.config[_org_header]['Port']),
                        'CORE_PEER_CHAINCODEADDRESS={}:{}'.format(_peer_host, int(self.config[_org_header]['Port'])+1),
                        'CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:{}'.format(int(self.config[_org_header]['Port'])+1),
                        'CORE_PEER_GOSSIP_BOOTSTRAP={}:{}'.format('peer{}.{}.{}'.format(gossip_peer, _org_name, _domain),
                                                                  self.config[_org_header]['P{}port'.format(gossip_peer)]),
                        'CORE_PEER_GOSSIP_EXTERNALENDPOINT={}:{}'.format(_peer_host, self.config[_org_header]['Port']),
                        'CORE_PEER_LOCALMSPID={}MSP'.format(_org_name)
                    ],
                    'volumes': [
                        '/var/run/:/host/var/run/',
                        '../crypto-config/peerOrganizations/{}.{}/peers/{}/msp:'
                        '/etc/hyperledger/fabric/msp'.format(_org_name, _domain, _peer_host),
                        '../crypto-config/peerOrganizations/{}.{}/peers/{}/tls:'
                        '/etc/hyperledger/fabric/tls'.format(_org_name, _domain, _peer_host),
                        '{}:/var/hyperledger/production'.format(_peer_host),
                    ],
                    'ports': ['"{port}:{port}"'.format(port=self.config[_org_header]['Port'])]
                }
                _config[_peer_host] = peer
        _main_config['services'] = _config
        print(' * - updating docker-compose-base.yaml')
        with open(self.docker_compose_base_file, 'w') as _output_stream:
            yaml.dump(_main_config, _output_stream, default_flow_style=False)
        print(' * - parsing unknown character in yaml')
        self.tokenizer(self.docker_compose_base_file, '\"\'', '\"')
        self.tokenizer(self.docker_compose_base_file, '\'\"', '\"')
        print(' * - end')

    def docker_composer_ca(self):
        """Helps to generate ca yaml.

        :return: ca configuration
        """
        print('#################### Generating docker ca yaml ####################')
        _main_config = {
            'version': '2',
            'networks': {
                self.config['orderer']['Network']: None
            }
        }
        _lower_config = {}
        print(' * - updating ca for each org')
        for each_org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            _org_name = self.config['org{}'.format(each_org)]['Name']
            _domain = self.config['orderer']['Domain']
            _config = {
                'image': 'hyperledger/fabric-ca:$IMAGE_TAG',
                'environment': [
                    'FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server',
                    'FABRIC_CA_SERVER_CA_NAME=ca-{}'.format(self.config['org{}'.format(each_org)]['Name']),
                    'FABRIC_CA_SERVER_TLS_ENABLED=true',
                    'FABRIC_CA_SERVER_TLS_CERTFILE='
                    '/etc/hyperledger/fabric-ca-server-config/ca.{}.{}-cert.pem'.format(_org_name, _domain),
                    'FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/CA{}_PRIVATE_KEY'.format(each_org),
                    'FABRIC_CA_SERVER_PORT={}'.format(self.config['org{}'.format(each_org)]['CAport'])
                ],
                'ports': ['"{caport}:{caport}"'.format(caport=self.config['org{}'.format(each_org)]['CAport'])],
                'command': "sh -c 'fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.{}.{}-cert.pem --ca.keyfile /etc/hyperledger/fabric-ca-server-config/CA{}_PRIVATE_KEY -b admin:adminpw -d'".format(_org_name, _domain, each_org),
                'volumes':
                    [
                        ' ./crypto-config/peerOrganizations/{}.{}/ca/:/etc/hyperledger/fabric-ca-server-config'.format(_org_name, _domain)
                    ],
                'container_name': 'ca_peer{}'.format(_org_name),
                'networks': [
                    '{}'.format(self.config['orderer']['Network'])
                ]
            }
            _lower_config['ca{}'.format(each_org)] = _config
        _main_config['services'] = _lower_config
        print(' * - updating docker-compose-ca.yaml')
        with open(self.docker_compose_ca_file, 'w') as _output_stream:
            yaml.dump(_main_config, _output_stream, default_flow_style=False)
        print(' * - parsing unknown character in yaml')
        self.tokenizer(self.docker_compose_ca_file, ' null', '')
        self.tokenizer(self.docker_compose_ca_file, '\"\'', '\"')
        self.tokenizer(self.docker_compose_ca_file, '\'\"', '\"')
        print(' * - end')
        return _lower_config

    def docker_composer_e2e(self):
        """Helps to generate end to end configuration in yaml.

        :return: None
        """
        print('#################### Generating docker e2e yaml ####################')
        _main_config = {
            'version': '2',
            'networks': {
                self.config['orderer']['Network']: None
            }
        }
        print(' * - updating orderer config in yaml')
        _config = {}
        _volume_config = {}
        _orderer_config = {
            'extends': {
                'file': '{}'.format(self.docker_compose_base_file),
                'service': '{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'])
            },
            'container_name': '{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain']),
            'networks': [
                '{}'.format(self.config['orderer']['Network'])
            ]
        }
        _volume_config['{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'])] = None
        _config['{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'])] = _orderer_config
        print(' * - updating peer config in yaml')
        for each_org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            _org_header = 'org{}'.format(each_org)
            for each_peer in range(0, int(self.config[_org_header]['PeerCount'])):
                _host = 'peer{}.{}.{}'.format(each_peer, self.config[_org_header]['Name'],
                                              self.config['orderer']['Domain'])
                _lower_config = {
                    'container_name': _host,
                    'extends': {
                        'file': '{}'.format(self.docker_compose_base_file),
                        'service': _host
                    },
                    'networks': [
                        '{}'.format(self.config['orderer']['Network'])
                    ]
                }
                _config[_host] = _lower_config
                _volume_config[_host] = None
        _main_config['volumes'] = _volume_config
        _ca = self.docker_composer_ca()
        for each_key in _ca.keys():
            _config[each_key] = _ca[each_key]
        print(' * - updating cli config in yaml')
        _config['cli'] = self.docker_composer_cli()
        _main_config['services'] = _config
        print(' * - updating docker-compose-e2e.yaml file')
        with open(self.docker_compose_e2e_file, 'w') as _output_stream:
            yaml.dump(_main_config, _output_stream, default_flow_style=False)
        print(' * - parsing unknown character in yaml')
        self.tokenizer(self.docker_compose_e2e_file, ' null', '')
        self.tokenizer(self.docker_compose_e2e_file, '\"\'', '\"')
        self.tokenizer(self.docker_compose_e2e_file, '\'\"', '\"')
        print(' * - end')

    def docker_composer_couch(self):
        """Helps to generate couch yaml.

        :return: None
        """
        print('#################### Generating docker couch yaml ####################')
        _main_config = {
            'version': '2',
            'networks': {
                'byfn': None
            }
        }
        couch_count = -1
        _basic_config = {}
        print(' * - updating couch DB for each peer')
        for each_org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            _org_header = 'org{}'.format(each_org)
            _org_name = self.config[_org_header]['Name']
            _domain = self.config['orderer']['Domain']
            for each_peer in range(0, int(self.config[_org_header]['PeerCount'])):
                couch_count += 1
                _peer_host = 'peer{}.{}.{}'.format(each_peer, _org_name, _domain)
                _port = self.config[_org_header]['DBP{}port'.format(each_peer)]
                _couch = {
                    'container_name': 'couchdb{}'.format(couch_count),
                    'image': 'hyperledger/fabric-couchdb',
                    'environment': [
                        'COUCHDB_USER=',
                        'COUCHDB_PASSWORD='
                    ],
                    'ports': ['"{port}:{port}"'.format(port=_port)],
                    'networks': ['byfn']
                }
                _peer = {
                    'environment': [
                        'CORE_LEDGER_STATE_STATEDATABASE=CouchDB',
                        'CORE_LEDGER_STATE_COUCHDBCONFIG_COUCHDBADDRESS='
                        '{}:{}'.format('couchdb{}'.format(couch_count), _port),
                        'CORE_LEDGER_STATE_COUCHDBCONFIG_USERNAME=',
                        'CORE_LEDGER_STATE_COUCHDBCONFIG_PASSWORD='
                    ],
                    'depends_on': ['couchdb{}'.format(couch_count)]
                }
                _basic_config['couchdb{}'.format(couch_count)] = _couch
                _basic_config[_peer_host] = _peer
        _main_config['services'] = _basic_config
        print(' * - updating docker compose couch yaml')
        with open(self.docker_compose_couch_file, 'w') as _output_stream:
            yaml.dump(_main_config, _output_stream, default_flow_style=False)
        print(' * - parsing unknown character in the yaml')
        self.tokenizer(self.docker_compose_couch_file, ' null', '')
        self.tokenizer(self.docker_compose_couch_file, '\"\'', '\"')
        self.tokenizer(self.docker_compose_couch_file, '\'\"', '\"')
        print(' * - end')

    def docker_composer_cli(self):
        """Helps to generate cli configuration.

        :return: cli configuration
        """
        print('#################### Generating docker cli configuration ####################')
        _org_header = 'org{}'.format(self.config['cli']['Org'])
        _org_name = '{}'.format(self.config[_org_header]['Name'])
        _domain = self.config['orderer']['Domain']
        _peer_address = 'peer{}.{}.{}:{}'.format(self.config['cli']['Peer'],
                                                 _org_name, _domain,
                                                 self.config[_org_header]['P{}port'.format(self.config['cli']['Peer'])])
        volumes = ['{}.{}'.format(self.config['orderer']['HostName'], self.config['orderer']['Domain'])]
        print(' * - updating cli configuration')
        for each_org in range(1, int(self.config['orderer']['Number_of_org'])+1):
            peer_count = int(self.config['org{}'.format(each_org)]['PeerCount'])
            for each_peer in range(0, peer_count):
                _peer_host = 'peer{}.{}.{}'.format(each_peer, _org_name, _domain)
                volumes.append(_peer_host)
        _basic_config = {
            'container_name': 'cli',
            'image': 'hyperledger/fabric-tools:$IMAGE_TAG',
            'tty': True,
            'stdin_open': True,
            'environment': [
                'SYS_CHANNEL=$SYS_CHANNEL',
                'GOPATH=/opt/gopath',
                'CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock',
                'FABRIC_LOGGING_SPEC=INFO',
                'CORE_PEER_ID=cli',
                'CORE_PEER_ADDRESS={}'.format(_peer_address),
                'CORE_PEER_LOCALMSPID={}MSP'.format(_org_name),
                'CORE_PEER_TLS_ENABLED=true',
                'CORE_PEER_TLS_CERT_FILE='
                '/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations'
                '/{}.{}/peers/{}/tls/server.crt'.format(_org_name, _domain, _peer_address),
                'CORE_PEER_TLS_KEY_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations'
                '/{}.{}/peers/{}/tls/server.key'.format(_org_name, _domain, _peer_address),
                'CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto'
                '/peerOrganizations/{}.{}/peers/{}/tls/ca.crt'.format(_org_name, _domain, _peer_address),
                'CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations'
                '/{org}.{domain}/users/Admin@{org}.{domain}/msp'.format(org=_org_name, domain=_domain)
            ],
            'working_dir': '/opt/gopath/src/github.com/hyperledger/fabric/peer',
            'command': '/bin/bash',
            'volumes': [
                '/var/run/:/host/var/run/',
                './../chaincode/:/opt/gopath/src/github.com/chaincode',
                './crypto-config:/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/',
                './scripts:/opt/gopath/src/github.com/hyperledger/fabric/peer/scripts/',
                './channel-artifacts:/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts'
            ],
            'depends_on': volumes,
            'networks': ['byfn']
        }
        print(' * - end')
        return _basic_config


if __name__ == '__main__':
    dc = DockerFiles()
    dc.docker_composer_base()
    # dc.docker_composer_ca()  # this has been taken care within e2e method itself.
    dc.docker_composer_couch()
    dc.docker_composer_e2e()
    print('-------------------------END------------------------------')
