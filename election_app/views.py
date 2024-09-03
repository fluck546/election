from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import ElectionRound, Candidate, Vote
from .forms import VoteForm
from django.utils import timezone
from web3 import Web3
import json
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Connect to Ethereum node using Infura
infura_url = 'https://sepolia.infura.io/v3/8829b151914a40b29dbfb359287f73b3'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Contract details
contract_address = '0x11564897bdAf32Fa8997167A6e4A1832345Fe2e1'
contract_abi = json.loads( """[
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
				"internalType": "string",
				"name": "_candidateName",
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
]""")

# Ensure connection to Ethereum node is successful
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

private_key = 'b228a7e0227f5af609b665efba1bb997d85f51666dcb2c8afe4a61528a75de6d'
account = w3.eth.account.from_key(private_key)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


@login_required
def vote_view(request, round_id):
    election_round = get_object_or_404(ElectionRound, id=round_id)
    candidates = Candidate.objects.filter(election_round=election_round)
    user = request.user 
    has_voted = Vote.objects.filter(voter=user, election_round=election_round).exists() 

    if has_voted:
        # Notify the user that they have already voted
        messages.warning(request, "You have already voted in this election round.")
        return render(request, 'vote.html', {'election_round': election_round, 'candidates': candidates, 'form': None, 'has_voted': True})

    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.election_round = election_round
            vote.voter = user  
            vote.save()

            # Add vote to blockchain
            
            tx = contract.functions.vote(
                election_round.id,
                vote.candidate.name
            ).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 2000000,
                'gasPrice': w3.to_wei('50', 'gwei')
            })
            
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Vote added with transaction hash: {tx_hash.hex()}")

            # Notify the user that their vote was successfully cast
            messages.success(request, "Thank you for voting!")

            return redirect('results', round_id=round_id)
    else:
        form = VoteForm()

    return render(request, 'vote.html', {'election_round': election_round, 'candidates': candidates, 'form': form, 'has_voted': False})



def get_candidates_from_blockchain(round_id):
    round_data = contract.functions.getElectionRound(round_id).call()
    candidate_count = round_data[5]  # Assuming the sixth element is the candidate count
    candidates = []
    for i in range(1, candidate_count + 1):
        candidate = contract.functions.getCandidate(round_id, i).call()
        candidates.append(candidate)
    return candidates


def results_view(request, round_id):
    election_round = get_object_or_404(ElectionRound, id=round_id)
    blockchain_candidates = get_candidates_from_blockchain(round_id)
    results = []
    for candidate_data in blockchain_candidates:
        candidate_id, candidate_name, candidate_votes = candidate_data
        results.append({
            'candidate': {
                'id': candidate_id,
                'name': candidate_name
            },
            'votes': candidate_votes
        })

    return render(request, 'results.html', {'election_round': election_round, 'results': results})

