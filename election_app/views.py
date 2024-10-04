from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.shortcuts import render, redirect, get_object_or_404

from .models import ElectionRound, Candidate, Vote
from faceRecognition.models import User
from .forms import  CustomUserForm, ElectionRoundForm, CandidateForm
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
import logging
from django.contrib.auth import logout,authenticate, login



logger = logging.getLogger(__name__)

def results_selection_page(request):
    rounds = ElectionRound.objects.all()
    return render(request, 'results_selection.html', {'rounds': rounds})

def encrypt_voter_name(voter_name, key):
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(voter_name.encode()) + padder.finalize()

    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return iv + encrypted_data


# Connect to Ethereum node using Infura
infura_url = "https://holesky.infura.io/v3/8829b151914a40b29dbfb359287f73b3"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Contract details
contract_address = "0x8A00c34d415D2b13eEFE0Cd85d8d0A9dAa4457b2"
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
]"""
)

# Ensure connection to Ethereum node is successful
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ethereum node")

private_key = "b228a7e0227f5af609b665efba1bb997d85f51666dcb2c8afe4a61528a75de6d"
account = w3.eth.account.from_key(private_key)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from .pdf_utils import generate_results_pdf

def download_pdf_results(request, round_id):
    
    # Ensure you are passing the request and round_id to the PDF generation function
    return generate_results_pdf(request, round_id)


@login_required(login_url="login_select")
def index(request):
    user = request.user
    if user.is_staff:
        return redirect("manage_users")

    # Get current time and filter active and past election rounds
    now = timezone.now()
    active_rounds = ElectionRound.objects.filter(start_date__lte=now, end_date__gte=now)
    all_rounds = ElectionRound.objects.filter(end_date__lt=now)
    rounds_with_vote_status = []

    # Prepare the data for active rounds and voting status
    for round in active_rounds:
        candidates = Candidate.objects.filter(election_round=round)
        has_voted = Vote.objects.filter(voter=user, election_round=round).exists()
        rounds_with_vote_status.append({
            "name": round.name,
            "id": round.id,
            "end_date": round.end_date,
            "user_has_voted": has_voted,
            "candidates": candidates,
        })

    if request.method == "POST":
        round_id = request.POST.get("round_id")
        candidate_id = request.POST.get("candidate_id")
        
        try:
            # Fetch the election round and candidate
            election_round = get_object_or_404(ElectionRound, id=round_id)
            candidate = get_object_or_404(Candidate, id=candidate_id)
            
            # Check if the user has already voted
            if not Vote.objects.filter(voter=user, election_round=election_round).exists():
                # Create a vote in the database
                vote = Vote.objects.create(
                    voter=user, election_round=election_round, candidate=candidate
                )
                
                # Encrypt the voter's name
                key = os.urandom(32)
                encrypted_voter_name = encrypt_voter_name(user.name, key)
                encrypted_voter_name_hex = encrypted_voter_name.hex()

                # Blockchain interaction
                account = w3.eth.account.from_key(private_key)
                
                # Retry logic for gas price and nonce management
                success = False
                attempts = 0
                max_attempts = 5  # Number of retry attempts
                while not success and attempts < max_attempts:
                    try:
                        nonce = w3.eth.get_transaction_count(account.address, 'pending')
                        gas_price = w3.eth.gas_price  # Fetch current gas price
                        gas_price = int(gas_price * 1.5)  # Increase the gas price by 50%

                        # Build and sign the transaction
                        tx = contract.functions.vote(
                            election_round.id, candidate.id, encrypted_voter_name_hex
                        ).build_transaction({
                            "from": account.address,
                            "nonce": nonce,
                            "gas": 2000000,
                            "gasPrice": gas_price,
                        })
                        signed_tx = account.sign_transaction(tx)
                        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                        
                        # Wait for the transaction receipt
                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
                        
                        # If transaction succeeds
                        success = True
                        messages.success(request, "ขอบคุณที่โหวต")
                    
                    except Exception as e:
                        logger.error(f"Blockchain transaction error: {str(e)}")
                        attempts += 1
                        if attempts == max_attempts:
                            messages.error(request, "ไม่สามารถดำเนินการโหวตได้ ลองใหม่อีกครั้งในภายหลัง")
                            return redirect("index")
                        else:
                            # If gas price is the issue, increase it for the next attempt
                            gas_price = int(gas_price * 1.2)  # Increase gas price for the next attempt
                
            else:
                messages.warning(request, "คุณได้โหวตรอบนี้ไปเเล้ว")

            return redirect("index")

        except Exception as e:
            logger.error(f"Error processing vote or fetching data: {str(e)}")
            messages.error(request, f"Error processing vote on the blockchain: {str(e)}")
            return redirect("index")

    return render(
        request,
        "index.html",
        {"rounds": rounds_with_vote_status, "all_rounds": all_rounds},
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


# staff section
def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff)(view_func)
    return decorated_view_func


import csv
# List and Create Views for User
@staff_required
def manage_users(request):
    users = User.objects.all().order_by('-id')
    # Handle file upload and CSV import
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'ไฟล์นี้ใช้งานไม่ได้')
            return redirect('manage_users')

        file_data = csv_file.read().decode("utf-8")
        csv_data = csv.reader(file_data.splitlines())
        next(csv_data)  # Skip the header

        try:
            for row in csv_data:
                sid, name, last_name, branch, is_staff = row
                # Add other fields as necessary, and ensure they match your model
                
                # Create user or handle duplicates
                if not User.objects.filter(sid=sid).exists():
                    User.objects.create(
                        sid=sid,
                        name=name,
                        last_name=last_name,
                        branch=branch,
                        is_staff=False,
                        is_active=False
                    )
            messages.success(request, 'เพิ่มผู้ใช้เรียบร้อยแล้ว')
            
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {str(e)}")
            return redirect('manage_users')

    


    return render(
        request, 
        'manage_users.html', 
        {'users': users}
    )


# Edit and Delete View for User
@staff_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.sid = request.POST["sid"]
        user.name = request.POST["name"]
        user.last_name = request.POST["last_name"]
        user.branch = request.POST["branch"]
        user.is_staff = "is_staff" in request.POST

        user.save()
        messages.success(request, "แก้ไขผู้ใช้รายนี้แล้ว")
        return redirect("manage_users")

    return render(request, "edit_user.html", {"user": user})


@staff_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "ลบผู้ใช้รายนี้เเล้ว")
    return redirect("manage_users")


# round management
@staff_required
def manage_rounds(request):
    rounds = ElectionRound.objects.all().order_by('-id')

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
            messages.success(request, 'เพิ่มรอบการเลือกตั้งแล้ว.')
            return redirect("manage_rounds")
    else:
        form = ElectionRoundForm()

    return render(
        request,
        "manage_rounds.html",
        {"rounds": rounds, "search_query": search_query, "form": form},
    )


@staff_required
def edit_round(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)

    if request.method == "POST":
        form = ElectionRoundForm(request.POST, instance=round)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขรอบการเลือกตั้งแล้ว.')
            return redirect("manage_rounds")
        
    else:
        form = ElectionRoundForm(instance=round)

    return render(request, "edit_round.html", {"form": form, "round": round})


@staff_required
def delete_round(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)
    round.delete()
    messages.success(request, "ลบรอบการเลือกตั้งเเล้ว")
    return redirect("manage_rounds")


# manage candidate
@staff_required
def manage_candidates(request):
    election_rounds = ElectionRound.objects.all().order_by('-id')
    
    search_query = request.GET.get("search_query", "")
    if search_query:
        candidates = Candidate.objects.filter(name__icontains=search_query)
        
    else:
        
        candidates = Candidate.objects.all()

    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate_obj = form.save()
            tx_receipt = add_candidate_to_blockchain(
                candidate_obj.election_round.id, candidate_obj.name
            )
            if tx_receipt:
                print(
                    f"Candidate added with transaction hash: {tx_receipt.transactionHash.hex()}"
                )
            messages.success(request, 'เพิ่มผู้สมัครแล้ว')
            return redirect("manage_candidates")
    else:
        form = CandidateForm()

    return render(
        request,
        "manage_candidates.html",
        {"candidates": candidates, "form": form, "election_rounds": election_rounds, "search_query": search_query},
    )


@staff_required
def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES, instance=candidate)  
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขผู้สมัครแล้ว')
            
            return redirect(manage_candidates)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)




@staff_required
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    messages.success(request, "ลบรายชื่อผู้สมัครแล้ว")
    return redirect("manage_candidates")


@staff_required
def add_user(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "เพิ่มผู้ใช้เรียบร้อยแล้ว")
            return redirect("manage_users")
        else:
            messages.error(request, "เพิ่มผู้ใช้ไม่สำเร็จ")
    else:
        form = CustomUserForm()
    return render(request, {"form": form})


@staff_required
def get_round_data(request, round_id):
    round = get_object_or_404(ElectionRound, id=round_id)
    data = {
        "name": round.name,
        "start_date": round.start_date.strftime("%Y-%m-%dT%H:%M"),  # Correct format for datetime-local input
        "end_date": round.end_date.strftime("%Y-%m-%dT%H:%M"),      # Correct format for datetime-local input
    }
    return JsonResponse(data)



@staff_required
def get_candidate_data(request, candidate_id):
    try:
        candidate = get_object_or_404(Candidate, id=candidate_id)
        data = {
            "number": candidate.number,
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


@staff_required
def get_user_data(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user_data = {
        "sid": user.sid,
        "name": user.name,
        "last_name": user.last_name,
        "branch": user.branch,
        "is_staff": user.is_staff,
    }
    return JsonResponse(user_data)



from django.db.models import Count

@staff_required
def manage_votes(request):
    # Perform search based on candidate name, if provided
    search_query = request.GET.get("search_query", "")
    if search_query:
        
        rounds = ElectionRound.objects.filter(candidates__name__icontains=search_query).distinct().order_by('-id')
    else:
        # Get all rounds with aggregated vote counts for each candidate
        rounds = ElectionRound.objects.prefetch_related('candidates').all().order_by('-id')

    return render(
        request, 
        "manage_votes.html", 
        {"rounds": rounds, "search_query": search_query}
    )


@staff_required
def get_round_votes(request, round_id):
    try:
        # Get the election round by ID
        election_round = get_object_or_404(ElectionRound, id=round_id)
        
        # Fetch candidates and their votes from the blockchain
        blockchain_candidates = get_candidates_from_blockchain(round_id)
        
        vote_data = []
        total_votes = 0  # Track total votes for the round
        
        for candidate_data in blockchain_candidates:
            candidate_id, candidate_name, candidate_votes = candidate_data
            
            # Try to find candidate in the local database, or log an error
            try:
                candidate = Candidate.objects.get(id=candidate_id)
            except Candidate.DoesNotExist:
                print(f"Error: Candidate with ID {candidate_id} does not exist.")
                continue

            total_votes += candidate_votes  # Sum up the votes for each candidate
            
            vote_data.append({
                'name': candidate.name,
                'last_name': candidate.last_name,
                'total_votes': candidate_votes  # From the blockchain data
            })
        
        # Return the round details with the total votes, start date, and end date
        return JsonResponse({
            'vote_data': vote_data,
            'total_votes': total_votes,
            'start_date': election_round.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': election_round.end_date.strftime('%Y-%m-%d %H:%M:%S'),
        }, status=200)
    
    except Exception as e:
        print(f"Error fetching round votes: {e}")
        return JsonResponse({'error': 'Failed to load votes'}, status=500)
    
def custom_logout(request):
    logout(request)
    return redirect("login_select")

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)
            return redirect('index')  # Redirect to the admin dashboard
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid credentials'})

    return render(request, 'admin_login.html')