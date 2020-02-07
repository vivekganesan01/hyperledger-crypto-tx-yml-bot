#!/bin/bash

ORDERER_GENESIS_PROFILE=OrgsOrdererGenesis
SYS_CHANNEL=my-sys-channel-name
CHANNEL_NAME=my-channel
CHANNEL_PROFILE_NAME=OrgsChannel
ORG_NAMES=cts tcs

# step 1:  setup the environmental variable
echo "#########################################################"
echo "#########  Setting up env variables #####################"
echo "##########################################################"
export PATH=${PWD}/../bin:${PWD}:$PATH  # bin has all the tools
export FABRIC_CFG_PATH=${PWD}

# THIS IS NOT NEEDED SINCE IT HAS BEEN TAKEN CARE WITHIN THE autogen.sh
## step 2: create certificate for org and component in the organisation
#echo "##########################################################"
#echo "##### Generate certificates using cryptogen tool #########"
#echo "##########################################################"
#cryptogen generate --config=./crypto-config.yaml
#echo
#echo
# step 3
echo "##########################################################"
echo "##### Generate genesis block #############################"
echo "##########################################################"
echo
configtxgen -profile ${GENESIS_ORDERER_PROFILE} -channelID ${SYS_CHANNEL} -outputBlock ./channel-artifacts/genesis.block
echo
# step 4
echo "##########################################################"
echo "##### Generate channel configuration #####################"
echo "##########################################################"
echo
configtxgen -profile ${CHANNEL_PROFILE_NAME} -outputCreateChannelTx ./channel-artifacts/channel.tx -channelID ${CHANNEL_NAME}
echo
# step 5
echo "##########################################################"
echo "##### Setting up anchor peer #############################"
echo "##########################################################"
echo
for org in ${ORG_NAMES}
do 
    echo "###### UPDATING ANCHOR FOR ORG: ${org}"
    configtxgen -profile ${CHANNEL_PROFILE_NAME} -outputAnchorPeersUpdate ./channel-artifacts/${org}MSPanchors.tx -channelID ${CHANNEL_NAME} -asOrg ${org}MSP
done
echo "############################ END ##########################"