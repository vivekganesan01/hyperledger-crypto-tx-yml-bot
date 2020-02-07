#!/bin/bash


echo "#########################################################"
echo "#########  Setting up env variables #####################"
echo "##########################################################"
echo " * - exporting bin directory and current directory"
export PATH=${PWD}/../bin:${PWD}:$PATH  # bin has all the tools
export FABRIC_CFG_PATH=${PWD}

echo "#########################################################"
echo "###  Generating configtx.yaml & crypto-config.yaml ######"
echo "##########################################################"
python3 ./util/crypto_tx_generator.py

echo "##########################################################"
echo "##### Generate certificates using cryptogen tool #########"
echo "##########################################################"
cryptogen generate --config=./crypto-config.yaml

echo "##########################################################"
echo "#########  generating all docker-compose.yaml ###########"
echo "##########################################################"
python3 ./util/docker_yml_generator.py

echo "##########################################################"
echo "##### Generate connection-json/yaml files ################"
echo "##########################################################"
python3 ./util/connection_file_generator.py

echo "##########################################################"
echo "##### Replace private key ################"
echo "##########################################################"
echo "copying start-up.sh from original backup"
cp start-up.sh.bak start-up.sh
python3 ./util/update_private_keys.py



