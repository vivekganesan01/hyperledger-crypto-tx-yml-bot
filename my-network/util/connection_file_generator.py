# Module to create connection json and yaml files for each organization.
#
# __author__ : vivek ganesan <vivekganesan01@gmail.com>
#
import configparser
import json
import yaml


class ConnectionFile:
    """Creates connection files."""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def create_json(self):
        """Creates connection.json for all the organization

        :return: None
        """
        print('############################ CONNECTION JSON ######################')
        for each_org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            org_header = 'org{}'.format(each_org)
            org_name = self.config[org_header]['Name']
            domain_name = self.config['orderer']['Domain']
            print(' * - {}/{}/{}'.format(org_header, org_name, domain_name))
            ca_pem = 'crypto-config/peerOrganizations/{N}.{D}/ca/ca.{N}.{D}-cert.pem'.format(N=org_name, D=domain_name)
            peer_pem = 'crypto-config/peerOrganizations/{N}.{D}/tlsca/tlsca.{N}.{D}-cert.pem'.format(N=org_name,
                                                                                                     D=domain_name)
            basic_dict = {
                "name": "my-network-{}".format(org_name),
                "version": "1.0.0"
            }
            client = {
                "organization": org_name,
                "connection": {
                    "timeout": {
                        "peer": {
                            "endorser": "300"
                        }
                    }
                }
            }
            org_peer_name = []
            peers = {}
            for each in range(0, int(self.config[org_header]['peerCount'])):
                peer = "peer{}.{}.{}".format(each, org_name, domain_name)
                org_peer_name.append(peer)
                peers[peer] = {
                    "url": "grpcs://localhost:{}".format(self.config[org_header]['P{}port'.format(each)]),
                    "tlsCACerts": {
                        "path": peer_pem,
                    },
                    "grpcOPtions": {
                        "ssl-target-name-override": peer,
                        "hostnameOverride": peer
                    }
                }
            organizations = {
                org_name: {
                    "mspid": '{}MSP'.format(org_name),
                    "peers": org_peer_name,
                    "certificateAuthorities": ["ca.{}.{}".format(org_name, domain_name)]
                }
            }
            certificate_authorities = {
                "ca.{}.{}".format(org_name, domain_name): {
                    "url": "https://localhost:{}".format(self.config[org_header]['CAport']),
                    "caName": "ca-{}".format(org_name),
                    "tlsCACerts": {
                        "path": ca_pem,
                    },
                    "httpOptions": {
                        "verify": False
                    }
                }
            }
            print(' * - updating client')
            basic_dict['client'] = client
            print(' * - updating org')
            basic_dict['organizations'] = organizations
            print(' * - updating peers')
            basic_dict['peers'] = peers
            print(' * - updating CA')
            basic_dict['certificateAuthorities'] = certificate_authorities
            with open('connection-{}.json'.format(org_name), 'w') as outfile:
                json.dump(basic_dict, outfile, indent=4)
            print(' * - end.')

    def create_yaml(self):
        """Creates connection yaml files.

        :return: None
        """
        print('############################ CONNECTION YAML ######################')
        for each_org in range(1, int(self.config['orderer']['Number_of_org']) + 1):
            org_header = 'org{}'.format(each_org)
            org_name = self.config[org_header]['Name']
            domain_name = self.config['orderer']['Domain']
            print(' * - {}/{}/{}'.format(org_header, org_name, domain_name))
            ca_pem = 'crypto-config/peerOrganizations/{N}.{D}/ca/ca.{N}.{D}-cert.pem'.format(N=org_name, D=domain_name)
            peer_pem = 'crypto-config/peerOrganizations/{N}.{D}/tlsca/tlsca.{N}.{D}-cert.pem'.format(N=org_name,
                                                                                                     D=domain_name)
            basic_dict = {
                "name": "my-network-{}".format(org_name),
                "version": "1.0.0"
            }
            client = {
                "organization": org_name,
                "connection": {
                    "timeout": {
                        "peer": {
                            "endorser": "300"
                        }
                    }
                }
            }
            org_peer_name = []
            peers = {}
            for each in range(0, int(self.config[org_header]['peerCount'])):
                peer = "peer{}.{}.{}".format(each, org_name, domain_name)
                org_peer_name.append(peer)
                peers[peer] = {
                    "url": "grpcs://localhost:{}".format(self.config[org_header]['P{}port'.format(each)]),
                    "tlsCACerts": {
                        "path": peer_pem,
                    },
                    "grpcOPtions": {
                        "ssl-target-name-override": peer,
                        "hostnameOverride": peer
                    }
                }
            organizations = {
                org_name: {
                    "mspid": '{}MSP'.format(org_name),
                    "peers": org_peer_name,
                    "certificateAuthorities": ["ca.{}.{}".format(org_name, domain_name)]
                }
            }
            certificate_authorities = {
                "ca.{}.{}".format(org_name, domain_name): {
                    "url": "https://localhost:{}".format(self.config[org_header]['CAport']),
                    "caName": "ca-{}".format(org_name),
                    "tlsCACerts": {
                        "path": ca_pem,
                    },
                    "httpOptions": {
                        "verify": False
                    }
                }
            }
            print(' * - updating client')
            basic_dict['client'] = client
            print(' * - updating org')
            basic_dict['organizations'] = organizations
            print(' * - updating peers')
            basic_dict['peers'] = peers
            print(' * - updating CA')
            basic_dict['certificateAuthorities'] = certificate_authorities
            with open('connection-{}.yaml'.format(org_name), 'w') as outfile:
                yaml.dump(basic_dict, outfile, default_flow_style=False)
            print(' * - end.')


if __name__ == '__main__':
    cf = ConnectionFile()
    cf.create_json()
    cf.create_yaml()
