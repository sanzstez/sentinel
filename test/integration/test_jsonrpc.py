import pytest
import sys
import os
import re
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import config

from omegacoind import OmegaDaemon
from omegacoin_config import OmegaConfig


def test_omegacoind():
    config_text = OmegaConfig.slurp_config_file(config.omegacoin_conf)
    network = 'mainnet'
    is_testnet = False
    genesis_hash = u'0000041a9498884aa2506b9dc832af53de1cbee3dca196a8d7b4319ee3a0f27c'
    for line in config_text.split("\n"):
        if line.startswith('testnet=1'):
            network = 'testnet'
            is_testnet = True
            genesis_hash = u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'

    creds = OmegaConfig.get_rpc_creds(config_text, network)
    omegacoind = OmegaDaemon(**creds)
    assert omegacoind.rpc_command is not None

    assert hasattr(omegacoind, 'rpc_connection')

    # Omega testnet block 0 hash == 0000041a9498884aa2506b9dc832af53de1cbee3dca196a8d7b4319ee3a0f27c
    # test commands without arguments
    info = omegacoind.rpc_command('getinfo')
    info_keys = [
        'blocks',
        'connections',
        'difficulty',
        'errors',
        'protocolversion',
        'proxy',
        'testnet',
        'timeoffset',
        'version',
    ]
    for key in info_keys:
        assert key in info
    assert info['testnet'] is is_testnet

    # test commands with args
    assert omegacoind.rpc_command('getblockhash', 0) == genesis_hash
