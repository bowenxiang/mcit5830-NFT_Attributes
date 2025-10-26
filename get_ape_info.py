from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)

# You will need the ABI to connect to the contract
# The file 'abi.json' has the ABI for the bored ape contract
# In general, you can get contract ABIs from etherscan
# https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('ape_abi.json', 'r') as f:
    abi = json.load(f)

############################
# Connect to an Ethereum node
api_url = "https://eth-mainnet.g.alchemy.com/v2/WMoV3ya-pyB8BLRr2aPrG"  # YOU WILL NEED TO PROVIDE THE URL OF AN ETHEREUM NODE
provider = HTTPProvider(api_url)
web3 = Web3(provider)


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    
    # Step 1: Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=abi)
    
    # Step 2: Get the owner of the NFT
    owner = contract.functions.ownerOf(ape_id).call()
    data['owner'] = owner
    
    # Step 3: Get the tokenURI
    token_uri = contract.functions.tokenURI(ape_id).call()
    
    # Step 4: Convert IPFS URI to HTTP gateway URL
    # tokenURI returns something like: ipfs://QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/1
    if token_uri.startswith('ipfs://'):
        # Remove 'ipfs://' prefix
        ipfs_hash = token_uri.replace('ipfs://', '')
        # Use Pinata gateway with API key
        metadata_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    else:
        metadata_url = token_uri
    
    # Step 5: Fetch metadata from IPFS
    headers = {
        'pinata_api_key': '3ba5786bb6e8e2619f14'
    }
    response = requests.get(metadata_url, headers=headers)
    metadata = response.json()
    
    # Step 6: Extract image URI
    data['image'] = metadata['image']
    
    # Step 7: Extract eyes attribute from attributes list
    attributes = metadata.get('attributes', [])
    for attribute in attributes:
        if attribute.get('trait_type') == 'Eyes':
            data['eyes'] = attribute.get('value')
            break

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data