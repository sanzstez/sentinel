#!/bin/bash
set -evx

mkdir ~/.omegacoincore

# safety check
if [ ! -f ~/.omegacoincore/.omegacoin.conf ]; then
  cp share/omegacoin.conf.example ~/.omegacoincore/omegacoin.conf
fi
