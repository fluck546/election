from web3 import Web3

import os
import json
from django.utils import timezone
from web3.exceptions import TransactionNotFound, TimeExhausted
import configparser


config = configparser.ConfigParser()
config.read('config.ini')

# Accessing a value
private_key_value = str(config['settings']['private_key']).strip()




# Load environment variables
infura_url = os.getenv('INFURA_URL','https://holesky.infura.io/v3/8829b151914a40b29dbfb359287f73b3')
w3 = Web3(Web3.HTTPProvider(infura_url))
private_key = os.getenv('PRIVATE_KEY',private_key_value)
contract_address = os.getenv('CONTRACT_ADDRESS','0xb5a9530F9be3F077492Df27241F7c8fAD47cf53d')
account_address = w3.eth.account.from_key(private_key)

contract_abi = json.loads("""[
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_candidateId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_lastName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_detail",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_branch",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_year",
				"type": "uint256"
			}
		],
		"name": "addCandidate",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_startDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_endDate",
				"type": "uint256"
			}
		],
		"name": "addElectionRound",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_candidateId",
				"type": "uint256"
			}
		],
		"name": "deleteCandidate",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			}
		],
		"name": "deleteElectionRound",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_candidateId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_newName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_newLastName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_newDetail",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_newBranch",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_newYear",
				"type": "uint256"
			}
		],
		"name": "editCandidate",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_newName",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_newStartDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_newEndDate",
				"type": "uint256"
			}
		],
		"name": "editElectionRound",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_candidateId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "encryptedVoterName",
				"type": "string"
			}
		],
		"name": "vote",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "voter",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "roundId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "candidateId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "encryptedVoterName",
				"type": "string"
			}
		],
		"name": "VoteCast",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "candidates",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "lastName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "detail",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "branch",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "year",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "voteCount",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "electionRoundCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "electionRounds",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "startDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "endDate",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "candidateCount",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "absentVotes",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_candidateId",
				"type": "uint256"
			}
		],
		"name": "getCandidate",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			}
		],
		"name": "getElectionRound",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_roundId",
				"type": "uint256"
			}
		],
		"name": "getUserVotes",
		"outputs": [
			{
				"internalType": "uint256[]",
				"name": "",
				"type": "uint256[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "userVotes",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]""")

# Connect to Ethereum node

contract = w3.eth.contract(address=contract_address, abi=contract_abi)
account = w3.eth.account.from_key(private_key)


def add_election_round_to_blockchain(roundID,name, start_date, end_date):
    attempts = 0
    max_attempts = 5  # Maximum number of retry attempts
    gas_price = w3.to_wei('50', 'gwei')  # Initial gas price
    start_date_utc = timezone.make_aware(start_date, timezone.utc) if timezone.is_naive(start_date) else start_date
    end_date_utc = timezone.make_aware(end_date, timezone.utc) if timezone.is_naive(end_date) else end_date

    while attempts < max_attempts:
        try:
            nonce = w3.eth.get_transaction_count(account.address, 'pending')

            tx = contract.functions.addElectionRound(
                roundID,
                name,
                int(start_date_utc.timestamp()),
                int(end_date_utc.timestamp())
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': gas_price
            })

            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # If transaction succeeds, return receipt
            return tx_receipt
        
        except Exception as e:
            print(f"Error adding election round to blockchain (attempt {attempts + 1}): {e}")
            attempts += 1
            gas_price = int(gas_price * 1.2)  # Increase gas price for the next attempt

    # If all attempts fail, return None
    print("Max retry attempts reached for adding election round to blockchain.")
    return None


def add_candidate_to_blockchain(round_id,candidate_id, name, last_name, detail, branch, year):
    attempts = 0
    max_attempts = 5  # Maximum retry attempts
    gas_price = w3.to_wei('50', 'gwei')  # Initial gas price

    while attempts < max_attempts:
        try:
            nonce = w3.eth.get_transaction_count(account.address, 'pending')

            tx = contract.functions.addCandidate(
                round_id,
                candidate_id,
                name,
                last_name,
                detail,
                branch,
                year
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': gas_price
            })

            signed_tx = w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # If transaction succeeds, return receipt
            return tx_receipt
        
        except Exception as e:
            print(f"Error adding candidate to blockchain (attempt {attempts + 1}): {e}")
            attempts += 1
            gas_price = int(gas_price * 1.2)  # Increase gas price for the next attempt

    # If all attempts fail, return None
    print("Max retry attempts reached for adding candidate to blockchain.")
    return None


def edit_candidate_on_blockchain(round_id, candidate_id, new_name, new_last_name, new_detail, new_branch, new_year):
    attempts = 0
    max_attempts = 5  # Maximum retry attempts
    gas_price = w3.to_wei('50', 'gwei')  # Initial gas price

    while attempts < max_attempts:
        try:
            nonce = w3.eth.get_transaction_count(account.address, 'pending')

            # Build the transaction for editing the candidate details
            tx = contract.functions.editCandidate(
                round_id,
                candidate_id,
                new_name,
                new_last_name,
                new_detail,
                new_branch,
                new_year
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 2000000,  # Adjust gas limit if needed
                'gasPrice': gas_price
            })

            # Sign the transaction
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)

            # Send the signed transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for the transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # If successful, return the transaction receipt
            return tx_receipt

        except (TransactionNotFound, TimeExhausted) as tx_error:
            # Specific handling for known exceptions
            print(f"Transaction error (attempt {attempts + 1}): {tx_error}")
            attempts += 1

        except Exception as e:
            # Handle any other exceptions
            print(f"Error editing candidate on blockchain (attempt {attempts + 1}): {e}")
            attempts += 1

        # Increase gas price by 20% for the next attempt
        gas_price = int(gas_price * 1.2)
        print(f"Increasing gas price for next attempt: {w3.from_wei(gas_price, 'gwei')} gwei")

    # If all attempts fail, return None
    print("Max retry attempts reached for editing candidate on blockchain.")
    return None

def edit_election_round_on_blockchain(round_id, new_name, new_start_date, new_end_date):
    attempts = 0
    max_attempts = 5  # Maximum retry attempts
    gas_price = w3.to_wei('50', 'gwei')  # Initial gas price

    while attempts < max_attempts:
        try:
            nonce = w3.eth.get_transaction_count(account.address, 'pending')

            # Build the transaction for editing the election round details
            tx = contract.functions.editElectionRound(
                round_id,
                new_name,
                new_start_date,
                new_end_date
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': 2000000,  # Adjust gas limit if needed
                'gasPrice': gas_price
            })

            # Sign the transaction
            signed_tx = w3.eth.account.sign_transaction(tx, private_key)

            # Send the signed transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Wait for the transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # If successful, return the transaction receipt
            return tx_receipt

        except (TransactionNotFound, TimeExhausted) as tx_error:
            # Specific handling for known exceptions
            print(f"Transaction error (attempt {attempts + 1}): {tx_error}")
            attempts += 1

        except Exception as e:
            # Handle any other exceptions
            print(f"Error editing election round on blockchain (attempt {attempts + 1}): {e}")
            attempts += 1

        # Increase gas price by 20% for the next attempt
        gas_price = int(gas_price * 1.2)
        print(f"Increasing gas price for next attempt: {w3.from_wei(gas_price, 'gwei')} gwei")

    # If all attempts fail, return None
    print("Max retry attempts reached for editing election round on blockchain.")
    return None