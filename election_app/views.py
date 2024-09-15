from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import ElectionRound, Candidate, Vote
from faceRecognition.models import CustomUser
from .forms import VoteForm, CustomUserForm, ElectionRoundForm, CandidateForm
from django.utils import timezone
from web3 import Web3
import json
from django.db import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from faceRecognition.views import facial_login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from .utils import add_election_round_to_blockchain, add_candidate_to_blockchain
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


def encrypt_voter_name(voter_name, key):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(voter_name.encode()) + padder.finalize()

    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_data


# Connect to Ethereum node using Infura
infura_url = "https://sepolia.infura.io/v3/8829b151914a40b29dbfb359287f73b3"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Contract details
contract_address = "0xD2ec278A02A5eb6BF6544936E30bc24D43492124"
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

# Ensure connection to Ethereum node is successful
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

private_key = "b228a7e0227f5af609b665efba1bb997d85f51666dcb2c8afe4a61528a75de6d"
account = w3.eth.account.from_key(private_key)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


@login_required
def vote_view(request, round_id):
    # Fetch election round and candidates
    election_round = get_object_or_404(ElectionRound, id=round_id)
    candidates = Candidate.objects.filter(election_round=election_round)
    user = request.user
    has_voted = Vote.objects.filter(voter=user, election_round=election_round).exists()
    # Check if the election round is active
    if not election_round.is_active:
        messages.warning(
            request,
            "This election round is not currently active. You cannot vote at this time.",
        )
        return render(
            request,
            "vote.html",
            {
                "election_round": election_round,
                "candidates": candidates,
                "form": None,
                "has_voted": False,
            },
        )
    # Check if the user has already voted
    if has_voted:
        messages.warning(request, "You have already voted in this election round.")
        return render(
            request,
            "vote.html",
            {
                "election_round": election_round,
                "candidates": candidates,
                "form": None,
                "has_voted": True,
            },
        )
    # Handle the voting form submission
    if request.method == "POST":
        form = VoteForm(request.POST, round_id=round_id)
        if form.is_valid():
            # Save the vote
            vote = form.save(commit=False)
            vote.election_round = election_round
            vote.voter = user
            vote.save()
            # Encrypt voter name
            key = os.urandom(32)
            candidate_id = vote.candidate.id
            encrypted_voter_name = encrypt_voter_name(user.username, key)
            encrypted_voter_name_hex = encrypted_voter_name.hex()

            try:
                # Send vote to blockchain
                tx = contract.functions.vote(
                    election_round.id,  # Pass the round ID
                    candidate_id,  # Candidate ID
                    encrypted_voter_name_hex,  # Encrypted Voter Name (hex)
                ).build_transaction(
                    {
                        "from": account.address,
                        "nonce": w3.eth.get_transaction_count(account.address),
                        "gas": 2000000,
                        "gasPrice": w3.to_wei("50", "gwei"),
                    }
                )

                # Sign and send transaction
                signed_tx = account.sign_transaction(tx)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                # Success message with transaction details
                messages.success(
                    request,
                    f"Thank you for voting! Transaction hash: {tx_hash.hex()} for candidate: {vote.candidate.name}",
                )
                return redirect("results", round_id=round_id)
            except Exception as e:
                # Handle blockchain transaction error
                messages.error(
                    request, f"Error processing vote on the blockchain: {str(e)}"
                )
                return redirect("vote_view", round_id=round_id)
        else:
            messages.error(request, "There was an issue with your submission.")
    else:

        form = VoteForm(round_id=round_id)

    # Render the voting form
    return render(
        request,
        "vote.html",
        {
            "election_round": election_round,
            "candidates": candidates,
            "form": form,
            "has_voted": False,
        },
    )


def get_candidates_from_blockchain(round_id):
    round_data = contract.functions.getElectionRound(round_id).call()
    candidate_count = round_data[5]
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
        results.append(
            {
                "candidate": {"id": candidate_id, "name": candidate_name},
                "votes": candidate_votes,
            }
        )

    return render(
        request, "results.html", {"election_round": election_round, "results": results}
    )


@login_required
def index(request):
    User = get_user_model()

    if request.user.is_authenticated:
        # If the user is staff, redirect to the manage_users page
        if request.user.is_staff:
            return redirect("manage_users")

        # Normal users continue with the normal election round selection
        active_rounds = ElectionRound.objects.filter(is_active=True)
        all_rounds = ElectionRound.objects.filter(is_active=False)

        return render(
            request,
            "round_selection.html",
            {"rounds": active_rounds, "all_rounds": all_rounds},
        )
    else:
        return redirect("facial_login")


# staff section
def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff)(view_func)
    return decorated_view_func


# List and Create Views for CustomUser
@staff_required
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, "manage_users.html", {"users": users})


# Edit and Delete View for CustomUser
@staff_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user.sid = request.POST["sid"]
        user.name = request.POST["name"]
        user.last_name = request.POST["last_name"]
        user.branch = request.POST["branch"]
        user.save()
        return redirect("manage_users")  # Redirect back to the user management page

    return render(request, "edit_user.html", {"user": user})


@staff_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect("manage_users")


# round management
@staff_required
def manage_rounds(request):
    rounds = ElectionRound.objects.all()

    if request.method == "POST":
        form = ElectionRoundForm(request.POST)
        if form.is_valid():
            round_obj = form.save()
            tx_receipt = add_election_round_to_blockchain(
                round_obj.name, round_obj.start_date, round_obj.end_date
            )
            if tx_receipt:
                print(
                    f"Election round added with transaction hash: {tx_receipt.transactionHash.hex()}"
                )
            return redirect("manage_rounds")
    else:
        form = ElectionRoundForm()

    return render(request, "manage_rounds.html", {"rounds": rounds, "form": form})


@staff_required
def edit_round(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)

    if request.method == "POST":
        form = ElectionRoundForm(request.POST, instance=round)
        if form.is_valid():
            form.save()
            return redirect(
                "manage_rounds"
            )  # Redirect to manage_rounds after updating the round
    else:
        form = ElectionRoundForm(instance=round)

    return render(request, "edit_round.html", {"form": form, "round": round})


@staff_required
def delete_round(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)
    round.delete()
    return redirect("manage_rounds")


# manage candidate
@staff_required
def manage_candidates(request):
    candidates = Candidate.objects.all()
    election_rounds = ElectionRound.objects.all()  # Fetch all election rounds

    if request.method == "POST":
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate_obj = form.save()
            tx_receipt = add_candidate_to_blockchain(
                candidate_obj.election_round.id, candidate_obj.name
            )
            if tx_receipt:
                print(
                    f"Candidate added with transaction hash: {tx_receipt.transactionHash.hex()}"
                )
            return redirect("manage_candidates")
    else:
        form = CandidateForm()

    return render(
        request,
        "manage_candidates.html",
        {"candidates": candidates, "form": form, "election_rounds": election_rounds},
    )


@staff_required
def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == "POST":
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect("manage_candidates")
    else:
        form = CandidateForm(instance=candidate)

    return render(
        request, "edit_candidate.html", {"form": form, "candidate": candidate}
    )


@staff_required
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    return redirect(
        "manage_candidates"
    )  # Redirect to manage_candidates after deleting the candidate


@staff_required
def get_user_data(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user_data = {
        "sid": user.sid,
        "name": user.name,
        "last_name": user.last_name,
        "branch": user.branch,
    }
    return JsonResponse(user_data)


@staff_required
def add_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User added successfully!")
            return redirect("manage_users")  # Redirect to the user management page
        else:
            messages.error(request, "Error adding user. Please check the form data.")
    else:
        form = CustomUserForm()
    return render(request, "add_user.html", {"form": form})


@staff_required
def get_round_data(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)
    data = {
        "name": round.name,
        "start_date": round.start_date.strftime("%Y-%m-%d"),
        "end_date": round.end_date.strftime("%Y-%m-%d"),
        "is_active": round.is_active,
    }
    return JsonResponse(data)


import logging

logger = logging.getLogger(__name__)

@staff_required
def get_candidate_data(request, candidate_id):
    try:
        candidate = get_object_or_404(Candidate, id=candidate_id)
        data = {
            "name": candidate.name,
            "last_name": candidate.last_name,
            "year": candidate.year,
            "branch": candidate.branch,
            "detail": candidate.detail,
            "election_round_id": candidate.election_round.id,
            "election_round_name": candidate.election_round.name,
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Failed to fetch candidate data for ID {candidate_id}: {str(e)}")
        return JsonResponse({"error": "Data fetch failed"}, status=500)



@staff_required
def get_election_rounds(request):
    rounds = ElectionRound.objects.all()
    rounds_data = [{"id": round.id, "name": round.name} for round in rounds]
    return JsonResponse({"election_rounds": rounds_data})
