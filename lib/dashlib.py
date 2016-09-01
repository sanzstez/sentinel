import pdb
from pprint import pprint
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
import base58
import hashlib
import re

def is_valid_dash_address( address, network = 'mainnet' ):
    # Only public key addresses are allowed
    # A valid address is a RIPEMD-160 hash which contains 20 bytes
    # Prior to base58 encoding 1 version byte is prepended and
    # 4 checksum bytes are appended so the total number of
    # base58 encoded bytes should be 25.  This means the number of characters
    # in the encoding should be about 34 ( 25 * log2( 256 ) / log2( 58 ) ).
    dash_version = 140 if network == 'testnet' else 76

    # Check length (This is important because the base58 library has problems
    # with long addresses (which are invalid anyway).
    if ( ( len( address ) < 26 ) or ( len( address ) > 35 ) ):
        return False

    address_version = None

    try:
        decoded = base58.b58decode_chk(address)
        address_version = ord(decoded[0])
    except:
        # rescue from exception, not a valid Dash address
        return False

    if ( address_version != dash_version ):
        return False

    return True


def hashit( data ):
    return int( hashlib.sha256(data).hexdigest(), 16 )

# returns the masternode VIN of the elected winner
def elect_mn(**kwargs):
    current_block_hash = kwargs['block_hash']
    mn_list = kwargs['mnlist']

    # filter only enabled MNs
    enabled = [mn for mn in mn_list if mn.status == 'ENABLED']
    block_hash_hash = hashit( current_block_hash )

    candidates = []
    for mn in enabled:
        mn_vin_hash = hashit( mn.vin )
        diff = mn_vin_hash - block_hash_hash
        absdiff = abs( diff )
        candidates.append({ 'vin': mn.vin, 'diff': absdiff })

    candidates.sort( key = lambda k: k['diff'] )

    try:
        winner = candidates[0]['vin']
    except:
        winner = None

    return winner


def parse_masternode_status_vin(status_vin_string):
    status_vin_string_regex = re.compile( 'CTxIn\(COutPoint\(([0-9a-zA-Z]+),\\s*(\d+)\),' )

    m = status_vin_string_regex.match( status_vin_string )
    txid = m.group(1)
    index = m.group(2)

    vin = txid + '-' + index
    if (txid == '0000000000000000000000000000000000000000000000000000000000000000'):
        vin = None

    return vin


# create superblock logic -- probably need a join table for proposal, superblock linkage
def create_superblock( proposals, event_block_height ):
    from models import Superblock, GovernanceObject, Proposal

    budget_allocated = Decimal(0)
    budget_total     = misc.get_superblock_budget_allocation()

    # TODO: probably use a sub-table to link proposals for RI
    payments = []
    for proposal in proposals:
        budget_allocated += proposal.payment_amount
        if budget_allocated > budget_total:
            break

        # TODO: probably use a sub-table to link proposals for RI
        payment = { 'address': proposal.payment_address,
                    'amount': proposal.payment_amount }
        payments.append( payment )

    # deterministic superblocks can't have random names
    sbname = "sb" + event_block_height

    # TODO: actually link this to Proposals in the DB and don't
    # actually include this info. This will enforce RI in the DB schema
    # also.
    sb = Superblock(
        superblock_name = sbname,
        event_block_height = event_block_height,
        payment_addresses = '|'.join( [pd['address'] for pd in payments] ),
        payment_amounts   = '|'.join( [pd['amount' ] for pd in payments] ),
    )

    return sb

def current_block_hash(dashd):
    height = dashd.rpc_command('getblockcount')
    block_hash = dashd.rpc_command('getblockhash', height)
    return block_hash

