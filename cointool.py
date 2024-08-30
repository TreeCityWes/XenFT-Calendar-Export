import json
from web3 import Web3
from tabulate import tabulate
from datetime import datetime, timedelta
from ics import Calendar, Event
import time
from collections import defaultdict
import sys
import random
import requests

def display_welcome_banner():
    banner = """
  _   _           _      
 | | | | __ _ ___| |__   
 | |_| |/ _` / __| '_ \  
 |  _  | (_| \__ \ | | | 
 |_| |_|\__,_|___/_| |_| 
 | | | | ___  __ _  __| |
 | |_| |/ _ \/ _` |/ _` |
 |  _  |  __/ (_| | (_| |
 |_| |_|\___|\__,_|\__,_|
                         
    Xen Batch Export for CoinTools
    Created by TreeCityWes.eth
    Visit HashHead.io
    #StayXen
    """
    print(banner)

# List of public Ethereum RPC endpoints
RPC_URLS = [
    "https://cloudflare-eth.com",
    "https://eth-rpc.gateway.pokt.network",
    "https://rpc.ankr.com/eth",
    "https://eth-mainnet.public.blastapi.io",
    "https://eth.llamanodes.com",
    "https://eth.drpc.org",
    "https://1rpc.io/eth",
    "https://main-light.eth.linkpool.io",
    "https://rpc.payload.de"
]

def get_web3():
    return Web3(Web3.HTTPProvider(random.choice(RPC_URLS)))

web3 = get_web3()

# Contract Addresses
COINTOOL_CONTRACT_ADDRESS = web3.to_checksum_address("0x0de8bf93da2f7eecb3d9169422413a9bef4ef628")
XEN_CONTRACT_ADDRESS = web3.to_checksum_address("0x06450dEe7FD2Fb8E39061434BAbCFC05599a6Fb8")

# ABIs
COINTOOL_CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}, {"internalType": "bytes", "name": "", "type": "bytes"}],
        "name": "map",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

XEN_CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "userMints",
        "outputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "uint256", "name": "term", "type": "uint256"},
            {"internalType": "uint256", "name": "maturityTs", "type": "uint256"},
            {"internalType": "uint256", "name": "rank", "type": "uint256"},
            {"internalType": "uint256", "name": "amplifier", "type": "uint256"},
            {"internalType": "uint256", "name": "eaaRate", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Load the contracts
cointool_contract = web3.eth.contract(address=COINTOOL_CONTRACT_ADDRESS, abi=COINTOOL_CONTRACT_ABI)
xen_contract = web3.eth.contract(address=XEN_CONTRACT_ADDRESS, abi=XEN_CONTRACT_ABI)

def calculate_proxy_address(cointool_address, salt, index, user_address):
    try:
        if isinstance(salt, str):
            salt = bytes.fromhex(salt.replace('0x', ''))
        derived_salt = Web3.solidity_keccak(['bytes', 'uint256', 'address'], [salt, index, web3.to_checksum_address(user_address)])
        bytecode = bytes.fromhex("3D602d80600A3D3981F3363d3d373d3D3D363d73") + Web3.to_bytes(hexstr=cointool_address) + bytes.fromhex("5af43d82803e903d91602b57fd5bf3")
        bytecode_hash = Web3.solidity_keccak(['bytes'], [bytecode])
        proxy_address = Web3.to_checksum_address(Web3.solidity_keccak(['bytes1', 'address', 'bytes32', 'bytes32'], [b'\xff', cointool_address, derived_salt, bytecode_hash])[-20:])
        return proxy_address
    except Exception as e:
        print(f"Error generating proxy address: {e}")
        return None

def get_mint_info(proxy_address):
    retries = 5
    while retries > 0:
        try:
            mint_info = xen_contract.functions.userMints(proxy_address).call()
            return mint_info
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 429:  # Too many requests
                print("Rate limit exceeded, switching to a new RPC endpoint...")
                time.sleep(1)
                global web3
                web3 = get_web3()  # Switch to a new RPC URL
                retries -= 1
            else:
                raise
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    return None

def calculate_vmus(user_address):
    vmu_data = defaultdict(lambda: defaultdict(int))
    total_vmus = 0
    processed_vmus = 0

    try:
        salts = ['0x01', '0x00']  # Add more if needed
        for salt in salts:
            salt_bytes = bytes.fromhex(salt[2:])
            salt_total_vmus = cointool_contract.functions.map(user_address, salt_bytes).call()
            total_vmus += salt_total_vmus
            print(f"Found {salt_total_vmus} VMUs for salt {salt}")
            
            if salt_total_vmus > 0:
                for i in range(1, salt_total_vmus + 1):
                    proxy_address = calculate_proxy_address(COINTOOL_CONTRACT_ADDRESS, salt, i, user_address)
                    if proxy_address:
                        mint_info = get_mint_info(proxy_address)
                        if mint_info and mint_info[0] != '0x0000000000000000000000000000000000000000':
                            maturity_date = time.strftime('%Y-%m-%d', time.localtime(mint_info[2]))
                            vmu_data[maturity_date]['count'] += 1
                            vmu_data[maturity_date]['term'] = mint_info[1]
                            vmu_data[maturity_date]['rank'] = mint_info[3]
                            vmu_data[maturity_date]['amplifier'] = mint_info[4]
                            vmu_data[maturity_date]['eaa_rate'] = mint_info[5]
                            vmu_data[maturity_date]['maturity_ts'] = mint_info[2]
                            
                            processed_vmus += 1
                            if processed_vmus % 10 == 0 or processed_vmus == total_vmus:
                                sys.stdout.write('\033[H\033[J')  # Clear the console
                                print(f"Processed {processed_vmus}/{total_vmus} VMUs")
                                print_vmu_table(vmu_data)

        print(f"Total VMUs found: {total_vmus}")
        return vmu_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def print_vmu_table(vmu_data):
    table_data = []
    for date, info in sorted(vmu_data.items()):
        table_data.append([
            date,
            info['count'],
            info['term'],
            info['rank'],
            info['amplifier'],
            info['eaa_rate']
        ])
    headers = ["Maturity Date", "VMU Count", "Term (days)", "Rank", "Amplifier", "EAA Rate"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print("\n")

def create_ics_file(vmu_data, filename="CT_Xen_Batch_Mints.ics"):
    calendar = Calendar()

    for date, info in vmu_data.items():
        maturity_datetime = datetime.fromtimestamp(info['maturity_ts'])
        
        event = Event()
        event.name = f"CT Xen Batch Due: {info['count']} VMUs"
        event.begin = maturity_datetime
        event.duration = timedelta(hours=1)
        event.description = f"{info['count']} VMUs mature. Rank: {info['rank']}, Amplifier: {info['amplifier']}, EAA Rate: {info['eaa_rate']}%"
        calendar.events.add(event)

    with open(filename, 'w') as f:
        f.write(str(calendar))
    
    print(f"\niCalendar file '{filename}' created.")

def display_menu():
    print("\n" + "─" * 30)
    print("│ CT Xen Batch Minting Menu")
    print("│" + "─" * 28)
    print("│ [1] View CT Xen Batch Mints")
    print("│ [2] Export Mints to Calendar File")
    print("│ [3] Exit")
    print("─" * 30)
    return input("│ Enter your choice: ")

def menu(user_address):
    while True:
        choice = display_menu()
        
        if choice == "1":
            vmu_data = calculate_vmus(user_address)
            if vmu_data:
                print_vmu_table(vmu_data)
        elif choice == "2":
            vmu_data = calculate_vmus(user_address)
            if vmu_data:
                create_ics_file(vmu_data)
        elif choice == "3":
            print("\nGoodbye!")
            exit(0)
        else:
            print("\nInvalid choice. Please select a valid option.")

if __name__ == "__main__":
    display_welcome_banner()
    user_address = web3.to_checksum_address(input("Enter your Ethereum address: "))
    menu(user_address)
