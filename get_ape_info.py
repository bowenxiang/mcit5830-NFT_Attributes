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
api_url = "https://cloudflare-eth.com" 
provider = HTTPProvider(api_url)
web3 = Web3(provider)


def get_ape_info(ape_id):
    assert isinstance(ape_id, int), f"{ape_id} is not an int"
    assert 0 <= ape_id, f"{ape_id} must be at least 0"
    assert 9999 >= ape_id, f"{ape_id} must be less than 10,000"

    data = {'owner': "", 'image': "", 'eyes': ""}

    # YOUR CODE HERE
    try:
        # 1. Set up the contract instance
        contract = web3.eth.contract(address=contract_address, abi=abi)
        
        # 2. Call the contract to get the owner
        data['owner'] = contract.functions.ownerOf(ape_id).call()
        
        # 3. Call the contract to get the tokenURI
        token_uri = contract.functions.tokenURI(ape_id).call()
        
        # 4. Convert the IPFS URI to an HTTP Gateway URL
        # We use the Pinata gateway as suggested: https://gateway.pinata.cloud/ipfs/
        # The token_uri is in the format "ipfs://HASH/ID"
        ipfs_hash_path = token_uri.split('//')[-1]
        
        metadata_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash_path}"
        
        # 5. Fetch the metadata from the IPFS gateway
        response = requests.get(metadata_url)
        response.raise_for_status()  # Raise an error for bad responses
        metadata = response.json()
        
        # 6. Extract the image URI from the metadata
        data['image'] = metadata.get('image', '')
        
        # 7. Extract the "Eyes" attribute from the metadata
        attributes = metadata.get('attributes', [])
        for attr in attributes:
            if attr.get('trait_type') == 'Eyes':
                data['eyes'] = attr.get('value', '')
                break  # Stop looping once we've found the 'Eyes' trait

    except Exception as e:
        print(f"An error occurred while fetching info for ape {ape_id}: {e}")
        # If an error occurs, the function will return the default 'data' dict with empty strings

    # END YOUR CODE

    assert isinstance(data, dict), f'get_ape_info{ape_id} should return a dict'
    assert all([a in data.keys() for a in
                ['owner', 'image', 'eyes']]), f"return value should include the keys 'owner','image' and 'eyes'"
    return data