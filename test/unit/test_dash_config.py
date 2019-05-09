import pytest
import os
import sys
import re
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
os.environ['SENTINEL_ENV'] = 'test'
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))
import config
from dash_config import DashConfig


@pytest.fixture
def dash_conf(**kwargs):
    defaults = {
        'rpcuser': 'user',
        'rpcpassword': 'pass',
        'rpcport': 3344,
    }

    # merge kwargs into defaults
    for (key, value) in kwargs.items():
        defaults[key] = value

    conf = """# basic settings
testnet=1 # TESTNET
server=1
rpcuser={rpcuser}
rpcpassword={rpcpassword}
rpcallowip=127.0.0.1
rpcport={rpcport}
""".format(**defaults)

    return conf


def test_get_rpc_creds():
    dash_config = dash_conf()
    creds = DashConfig.get_rpc_creds(dash_config, 'testnet')

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'user'
    assert creds.get('password') == 'pass'
    assert creds.get('port') == 3344

    dash_config = dash_conf(rpcpassword='pass', rpcport=3344)
    creds = DashConfig.get_rpc_creds(dash_config, 'testnet')

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'user'
    assert creds.get('password') == 'pass'
    assert creds.get('port') == 3344

    no_port_specified = re.sub('\nrpcport=.*?\n', '\n', dash_conf(), re.M)
    creds = DashConfig.get_rpc_creds(no_port_specified, 'testnet')

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'user'
    assert creds.get('password') == 'pass'
    assert creds.get('port') == 3344


def test_slurp_config_file():
    import tempfile

    dash_config = """# basic settings
#testnet=1 # TESTNET
server=1
printtoconsole=1
txindex=1 # enable transaction index
"""

    expected_stripped_config = """server=1
printtoconsole=1
txindex=1 # enable transaction index
"""

    with tempfile.NamedTemporaryFile(mode='w') as temp:
        temp.write(dash_config)
        temp.flush()
        conf = DashConfig.slurp_config_file(temp.name)
        assert conf == expected_stripped_config
