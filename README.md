
# XenFT Management Tool

This script allows users to manage their XenFTs across various EVM chains. Users can export their XenFTs to an `.ics` calendar file, display data on-screen, or select a different chain to manage their XenFTs.

## Features:

- Display a welcome banner.
- Fetch XenFTs from multiple EVM chains.
- Export XenFTs to an `.ics` file suitable for Google Calendar.
- Display XenFT data on-screen in a table format.
- Handle ENS domain names as input for Ethereum addresses.

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
python wenxen-allchains.py
```

4. Follow the on-screen instructions.

## Input:

- Enter your EVM address: This can be an Ethereum address (e.g., `0x1234...`) or an ENS domain name (e.g., `treecitywes.eth`).
  
- Select your EVM Chain: Choose from the list of supported chains. You can also select 'Search all chains' to fetch XenFTs from all chains.

- XenFT Management Menu: Here, you can choose to export your XenFTs to a calendar file, display them on-screen, go back to the chain selection, or exit the program.

## Output:

If you choose to export XenFTs to a calendar file, an `.ics` file will be generated in the script's directory. This file can be imported into Google Calendar or any other calendar application that supports the `.ics` format.
