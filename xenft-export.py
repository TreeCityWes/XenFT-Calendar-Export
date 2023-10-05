import json
import base64
from web3 import Web3
from tabulate import tabulate
from datetime import datetime, timedelta
from ics import Calendar, Event
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
web3 = Web3()

def display_welcome_banner():
    banner = """

██╗░░██╗███████╗███╗░░██╗███████╗████████╗  ███████╗██╗░░██╗██████╗░░█████╗░██████╗░████████╗
╚██╗██╔╝██╔════╝████╗░██║██╔════╝╚══██╔══╝  ██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝
░╚███╔╝░█████╗░░██╔██╗██║█████╗░░░░░██║░░░  █████╗░░░╚███╔╝░██████╔╝██║░░██║██████╔╝░░░██║░░░
░██╔██╗░██╔══╝░░██║╚████║██╔══╝░░░░░██║░░░  ██╔══╝░░░██╔██╗░██╔═══╝░██║░░██║██╔══██╗░░░██║░░░
██╔╝╚██╗███████╗██║░╚███║██║░░░░░░░░██║░░░  ███████╗██╔╝╚██╗██║░░░░░╚█████╔╝██║░░██║░░░██║░░░
╚═╝░░╚═╝╚══════╝╚═╝░░╚══╝╚═╝░░░░░░░░╚═╝░░░  ╚══════╝╚═╝░░╚═╝╚═╝░░░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░
Export XENFTs to an .ics file and import into Google Calendar
Created by TreeCityWes.eth - Visit HashHead.io to Buy me a Coffee
    """
    print(banner)


# Chain Configurations
CHAINS = {
    'Ethereum': {
        'rpc': 'https://eth.llamarpc.com',
        'contract': '0x0a252663DBCc0b073063D6420a40319e438Cfa59'
    },
    'BSC': {
        'rpc': 'https://binance.llamarpc.com',
        'contract': '0x1Ac17FFB8456525BfF46870bba7Ed8772ba063a5'
    },
    'Polygon': {
        'rpc': 'https://polygon.llamarpc.com',
        'contract': '0x726bB6aC9b74441Eb8FB52163e9014302D4249e5'
    },
    'Avalanche': {
        'rpc': 'https://rpc.ankr.com/avalanche',
        'contract': '0x94d9E02D115646DFC407ABDE75Fa45256D66E043'
    },
    'Ethereum POW': {
        'rpc': 'https://mainnet.ethereumpow.org',
        'contract': '0x94d9E02D115646DFC407ABDE75Fa45256D66E043'
    },
    'Moonbeam': {
        'rpc': 'https://rpc.ankr.com/moonbeam',
        'contract': '0x94d9E02D115646DFC407ABDE75Fa45256D66E043'
    },
    'EVMOS': {
        'rpc': 'https://evmos-evm.publicnode.com',
        'contract': '0x4c4CF206465AbFE5cECb3b581fa1b508Ec514692'
    },
    'Fantom': {
        'rpc': 'https://rpc.ankr.com/fantom',
        'contract': '0x94d9E02D115646DFC407ABDE75Fa45256D66E043'
    },
    'Pulsechain': {
        'rpc': 'https://rpc.pulsechain.com',
        'contract': '0xfEa13BF27493f04DEac94f67a46441a68EfD32F8'
    },
    'Optimism': {
        'rpc': 'https://optimism.llamarpc.com',
        'contract': '0xAF18644083151cf57F914CCCc23c42A1892C218e'
    },
    'Base': {
        'rpc': 'https://base.meowrpc.com',
        'contract': '0x379002701BF6f2862e3dFdd1f96d3C5E1BF450B6'
    }
}

# Load ABIs from JSON files
with open("xenft_abi.json", 'r') as f:
    xenft_abi = json.load(f)

def prompt_continue():
    input("\nPress Enter to continue...")

def get_attribute(data, attribute_name):
    return next((attr['value'] for attr in data.get('attributes', []) if attr['trait_type'] == attribute_name), "N/A")

def get_user_xenfts(account_address, xenft_contract, selected_chain):
    try:
        token_ids = xenft_contract.functions.ownedTokens().call({'from': account_address})
        xenft_details = []

        for token_id in token_ids:
            token_uri = xenft_contract.functions.tokenURI(token_id).call()

            if token_uri.startswith("data:application/json;base64,"):
                token_data = json.loads(base64.b64decode(token_uri.split(",")[1]))
            else:
                continue

            xenft = {
                'Name': f"{selected_chain} {token_data['name']}",
                'Class': get_attribute(token_data, 'Class'),
                'VMUs': get_attribute(token_data, 'VMUs'),
                'cRank': get_attribute(token_data, 'cRank'),
                'AMP': get_attribute(token_data, 'AMP'),
                'EAA (%)': get_attribute(token_data, 'EAA (%)'),
                'Maturity DateTime': get_attribute(token_data, 'Maturity DateTime'),
                'Term': get_attribute(token_data, 'Term'),
                'XEN Burned': get_attribute(token_data, 'XEN Burned'),
                'Category': get_attribute(token_data, 'Category')
            }
            xenft_details.append(xenft)

        xenft_details = sorted(xenft_details, key=lambda x: datetime.strptime(x['Maturity DateTime'], "%b %d, %Y %H:%M %Z"), reverse=True)
        
        # Print summary for each chain
        count = len(xenft_details)
        if count == 0:
            print(f"No tokens found for the given address on {selected_chain}.")
        else:
            print(f"Total of {count} found on {selected_chain}.")

        return xenft_details
    
    except Exception as e:
        print(f"Error in get_user_xenfts: {e}")
        return []

def display_menu():
    print("\n" + "─" * 25)
    print("│ XenFT Management Menu")
    print("│" + "─" * 23)
    print("│ [1] Export XenFTs to Calendar File")
    print("│ [2] Display Data On Screen Only")
    print("│ [3] Go back to chain selection")
    print("│ [4] Exit")
    print("─" * 25)
    return input("│ Enter your choice: ")

class ExitScript(Exception):
    pass

def menu(user_address, xenft_contract, selected_chain):
    xenfts = []
    while True:
        choice = display_menu()
        
        if selected_chain == "ALL_CHAINS":
            xenfts = all_xenfts
        else:
            xenfts = get_user_xenfts(user_address, xenft_contract, selected_chain)

        if choice == "1":
            create_ics_file(xenfts, selected_chain if selected_chain != "ALL_CHAINS" else "AllChains", f"{selected_chain}-XenFTs.ics" if selected_chain != "ALL_CHAINS" else "AllChains-XenFTs.ics")
            print(f"\niCalendar file '{selected_chain}-XenFTs.ics' created.")
        elif choice == "2":
            print(f"\nXenFTs for {user_address}:")
            print(tabulate(xenfts, tablefmt='grid'))
        elif choice == "3":
            return  
        elif choice == "4":
            print("\nGoodbye!")
            exit(0)  
        else:
            print("\nInvalid choice. Please select a valid option.")

def create_ics_file(xenfts, chain_name, filename="events.ics"):
    calendar = Calendar()

    for xenft in xenfts:
        if xenft['Maturity DateTime'] != "N/A":  
            maturity_datetime_str = xenft['Maturity DateTime']
            maturity_datetime = datetime.strptime(maturity_datetime_str, "%b %d, %Y %H:%M %Z")

            event = Event()
            event.name = f"{chain_name} XenFT Due: {xenft['Name']}"
            event.begin = maturity_datetime
            event.duration = timedelta(hours=1)
            event.description = f"{xenft['Name']} on {chain_name} reaches maturity."
            calendar.events.add(event)

    with open(filename, 'w') as f:
        f.write(str(calendar))

def select_chain():
    while True:
        print("\n" + "─" * 30)
        print("│ Select your EVM Chain:")
        print("│" + "─" * 28)
        print("│ [0] Search all chains")
        for idx, chain in enumerate(CHAINS.keys()):
            print(f"│ [{idx+1}] {chain}")
        print("│ [13] EXIT")  
        print("─" * 30)
        
        try:
            choice = int(input("│ Enter your choice: "))
            print("─" * 30 + "\n")
            if choice == 13:
                print("\nGoodbye!")
                exit(0)
            elif choice == 0:
                return "ALL_CHAINS"
            elif 1 <= choice <= len(CHAINS):
                return list(CHAINS.keys())[choice - 1]
            else:
                print("\nInvalid choice. Please select a valid option.")
        except ValueError:
            print("\nInvalid input. Please enter a number corresponding to your choice.")

if __name__ == "__main__":
    display_welcome_banner()  # Display banner when the program starts

    all_xenfts = []
    user_address = None
    
    # Keep prompting until a valid address is provided
    while not user_address:
        user_address_input = input("\nPlease enter your EVM address: ")

        if user_address_input.endswith('.eth'):
            # Resolve ENS address using Ethereum RPC
            eth_rpc_url = CHAINS['Ethereum']['rpc']
            eth_web3 = Web3(Web3.HTTPProvider(eth_rpc_url))
            user_address = eth_web3.ens.address(user_address_input)
            if not user_address:
                print("Failed to resolve ENS name. Please re-enter.")
                prompt_continue()
        elif web3.is_address(user_address_input) and web3.is_checksum_address(user_address_input):
            user_address = user_address_input
        else:
            print("Invalid address. Please re-enter.")
        
    while True:
        selected_chain = select_chain()
        
        if selected_chain == "ALL_CHAINS":
            for chain_name, chain_data in CHAINS.items():
                try:
                    rpc_url = chain_data['rpc']
                    web3 = Web3(Web3.HTTPProvider(rpc_url))
                    xenft_contract_address = web3.to_checksum_address(chain_data['contract'])
                    xenft_contract = web3.eth.contract(address=xenft_contract_address, abi=xenft_abi)
                    tokens_found = get_user_xenfts(user_address, xenft_contract, chain_name)
                    all_xenfts.extend(tokens_found)
                except Exception as e:
                    print(f"Error fetching data for {chain_name}. Error: {e}")
            menu(user_address, None, "ALL_CHAINS")
        else:
            rpc_url = CHAINS[selected_chain]['rpc']
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            xenft_contract_address = web3.to_checksum_address(CHAINS[selected_chain]['contract'])
            xenft_contract = web3.eth.contract(address=xenft_contract_address, abi=xenft_abi)
            
            try:
                menu(user_address, xenft_contract, selected_chain)
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                prompt_continue()
