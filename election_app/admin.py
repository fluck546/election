from django.contrib import admin
from .models import ElectionRound, Candidate, Vote
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Set up Web3 connection
infura_url = os.getenv(
    "INFURA_URL", "https://sepolia.infura.io/v3/8829b151914a40b29dbfb359287f73b3"
)
private_key = os.getenv(
    "PRIVATE_KEY", "b228a7e0227f5af609b665efba1bb997d85f51666dcb2c8afe4a61528a75de6d"
)
contract_address = os.getenv(
    "CONTRACT_ADDRESS", "0x990944A322a7F928aD3E1bC1B6640b4Ea171da5b"
)
account_address = os.getenv(
    "ACCOUNT_ADDRESS", "0xcAFa11cB0cf830426D66D868653f6FdC0128bb3C"
)
contract_abi = json.loads(
    """[
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
				"internalType": "bool",
				"name": "isActive",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "candidateCount",
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
				"internalType": "bool",
				"name": "",
				"type": "bool"
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
]"""
)

# Connect to Ethereum node using Infura
w3 = Web3(Web3.HTTPProvider(infura_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Ensure connection to Ethereum node is successful
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

# Create an account object using the private key
account = w3.eth.account.from_key(private_key)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1


class ElectionRoundAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    search_fields = ("name",)
    inlines = [CandidateInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:

            tx = contract.functions.addElectionRound(
                obj.name, int(obj.start_date.timestamp()), int(obj.end_date.timestamp())
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "gas": 2000000,
                    "gasPrice": w3.to_wei("50", "gwei"),
                }
            )
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Election round added with transaction hash: {tx_hash.hex()}")


class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "election_round")
    search_fields = ("name", "election_round__name")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            try:

                w3 = Web3(Web3.HTTPProvider(infura_url))

                if not w3.is_connected():
                    print("Failed to connect to Web3 provider")
                    return

                nonce = w3.eth.get_transaction_count(account_address)
                tx = contract.functions.addCandidate(
                    obj.election_round.id, obj.name
                ).build_transaction(
                    {
                        "from": account_address,
                        "nonce": nonce,
                        "gas": 200000,
                        "gasPrice": w3.to_wei("50", "gwei"),
                    }
                )

                signed_tx = w3.eth.account.sign_transaction(tx, private_key)

                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                if tx_receipt.status == 1:
                    print(f"Candidate added with transaction hash: {tx_hash.hex()}")
                else:
                    print(f"Transaction failed with status: {tx_receipt.status}")

                if tx_receipt.logs:
                    for log in tx_receipt.logs:
                        print(f"Log: {log}")
                candidate_id = 1
                candidate_info = contract.functions.getCandidate(
                    int(obj.election_round.id), candidate_id
                ).call()

                print(f"Candidate Info: {candidate_info}")

                if candidate_info:
                    print(
                        f"Candidate Details: ID: {candidate_info[0]}, Name: {candidate_info[1]}, Count: {candidate_info[2]}"
                    )
                    print("Candidate was successfully added to the blockchain.")
                else:
                    print("Candidate was not added to the blockchain.")
            except Exception as e:
                print(f"Error adding candidate to blockchain: {e}")


admin.site.register(ElectionRound, ElectionRoundAdmin)


try:
    admin.site.register(Candidate, CandidateAdmin)
except admin.sites.AlreadyRegistered:
    pass


admin.site.register(Vote)
