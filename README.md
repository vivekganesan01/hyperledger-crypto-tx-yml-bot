# Blockchain Hyperledger artifacts auto-generator

Auto-generates some of the hyperledger org level configuration yaml files and MSP key certs via cryptogen tool. Below are the list of files it auto-generates,

  - docker-compose-e2e.yaml
  - docker-compose-base.yaml
  - docker-compose-ca.yaml
  - docker-compose-couch.yaml
  - connection-{org}.yaml
  - connection-{org}.json
  - crypto-config.yaml
  - configtx.yaml

# Steps to generate:
### Installation

Note: Requires python 3.6+ to run.

Clone the repository:

```sh
$ git clone https://github.com/vivekganesan01/hyperledger_crypto_tx_yaml_bot.git
```

Edit the config.ini file:
   - Make a copy of the config_sample.ini to config.ini and update the organization details as per your requirement
   - In config.ini update fields for `orderer` and `organization`
   - It can hold `n` number of organization, so if you want to add new organization simple copy `[org1]` entire block
    and paste below
   - `[org{number}]` org section header should be always `[org1] [org2] [org3] .. [orgn]` in this syntax
   - parameter information: `PeerCount` = number of peers, `Port` = anchor peer, `P0port...Pnport` = peer port, 
    `CAport` = certificate authority port, `DBP0port....DBPnport` = couch DB port for peer 1,2...n
   - `[cli]` sections states to which organization and peer the cli connector should connect (i.e, updates e2e yaml)
   - `[channel]` sections specifies the `sys channel name, channel name, profile name, genesis profile name`
    make sure to update the default values if needed.

```sh
$ cd my-network
$ cp config_sample.ini config.ini
```

Run auto-generator:
   - generates all the yaml files
   - generates certificates under `crypto-config` folder
   - updates all the organization CA_PRIVATE_KEY in the yaml files

```sh
$ ./auto-generator.sh
```

Generate `anchor, genesis block, channel` configuration:

```sh
$ ./start-up.sh
```


### Development
This is a modified version of `byfn.sh` from hyperledger fabric `RELEASE v 1.4.3`. Refer to the original files if needed.

### Todos
 - Currently supports Hyperledger Release v1.4.3 and v1.4.4
 - Working to update for Release v2.0.0
 - Working on integrating new organization to an existing infrastructure
 - Working on re-writing this wrapper API with Go-Lang web interface
 - working on modifying the Start script of the network:

```sh
$ ./byfn.sh up
```

### Limitation
  - Supports only Hyperledger Release v1.4.3 and v1.4.4
  - Supports only couch DB
  - Supports only for only studies and POC projects
