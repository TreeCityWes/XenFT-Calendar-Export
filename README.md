
# XenFT Calendar Export Tool

This script allows users to export a list of their XenFTs across various EVM chains. Users can import reminders of all XenFTs into Google Calendar or other calendar software. 

## Features:

- Fetch XenFTs from multiple EVM chains.
- Export XenFTs to an `.ics` file suitable for Google Calendar.
- Display XenFT data on-screen in a table format.
- Supports ENS names as input for all chains.

## Supported EVM Chains:

Ethereum, BSC, Polygon, Avalanche, Ethereum POW, Moonbeam, EVMOS, Fantom, Pulsechain, Optimism, and Base.

## Prerequisites:

Ensure you have the following installed:

- Python 3.x
- web3.py
- tabulate
- ics

You can install the required packages using:

```bash
pip install web3 tabulate ics
```

## Usage:

1. Clone this repository.
2. Navigate to the directory containing the script.
3. Run the script using:

```bash
python xenft-export.py
```

4. Follow the on-screen instructions.

## Input:

- Enter your EVM address: This can be an Ethereum address (e.g., `0x1234...`) or an ENS domain name.
  
- Select your EVM Chain: Choose from the list of supported chains. You can also select 'Search all chains' to fetch XenFTs from all chains.

- XenFT Management Menu: Here, you can choose to export your XenFTs to a calendar file, display them on-screen, go back to the chain selection, or exit the program.

## Output:

If you choose to export XenFTs to a calendar file, an `.ics` file will be generated in the script's directory. This file can be imported into Google Calendar or any other calendar application that supports the `.ics` format.

Visit HashHead.io for more info! 
