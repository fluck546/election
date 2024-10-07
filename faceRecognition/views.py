import face_recognition
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
import random
import string
from io import BytesIO
from PIL import Image
import numpy as np
import json
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

def compare_faces(existing_face_encoding, new_face_encoding):
    return face_recognition.compare_faces([existing_face_encoding], new_face_encoding)[0]

def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff)(view_func)
    return decorated_view_func


def generate_random_password():
    """Generate a random password for the user."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))

def login_select(request):
    return render(request, 'login_select.html')

def generate_otp():
    """Generate a 6-digit OTP."""
    return "".join(random.choices(string.digits, k=6))


def send_otp_email_helper(email, otp="123456"):
    """Send an OTP to the user's email."""
    subject = 'Your OTP for Registration'
    message = f'Your OTP for completing registration is: {otp}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list)
        print(f"OTP sent to {email}")
        return True
    except Exception as e:
        print(f"Error while sending OTP: {e}")  # Log the exception
        return False

def send_otp_email(request):
    """Handle OTP sending via AJAX POST request."""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if not email:
            return JsonResponse({'error': 'Email is required.'}, status=400)
        
        otp = generate_otp()  # Generate a random OTP
        otp_sent = send_otp_email_helper(email, otp)
        if otp_sent:
            # Store OTP and related user info in the session for later verification
            request.session['otp_verification'] = {
                'email': email,
                'otp': otp
            }
            return JsonResponse({'success': 'OTP sent successfully.'})
        else:
            return JsonResponse({'error': 'Failed to send OTP. Please try again later.'}, status=500)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)



def register(request):
    if request.method == "POST":
        # Retrieve data from form
        sid = request.POST.get("sid")
        name = request.POST.get("name")
        last_name = request.POST.get("last_name")
        branch = request.POST.get("branch")
        email = request.POST.get("email")
        otp_input = request.POST.get("otp")
        captured_image_base64 = request.POST.get("image")

        # Check if the user exists with the given SID, name, last_name, branch, and email but is not yet active
        user = User.objects.filter(sid=sid, name=name, last_name=last_name, branch=branch, email=email, is_active=False).first()

        if not user:
            messages.error(request, "ไม่มีผู้ใช้ที่เข้าเงื่อนไขโปรดติดต่อผู้ดูแลระบบ")
            return render(request, "register.html")

        # Check if OTP is being verified
        if 'otp_verification' in request.session:
            otp_session = request.session.get('otp_verification')

            if not otp_input or otp_session['otp'] != otp_input:
                messages.error(request, "OTP ไม่ถูกต้องโปรดลองใหม่อีกครั้ง")
                return render(request, "register.html")

            # OTP matches, continue registration
            if captured_image_base64:
                # Process the image and extract face encoding
                image_processing_outcome = process_user_image(captured_image_base64)
                if image_processing_outcome.get('success'):
                    face_encoding = image_processing_outcome.get('face_encoding')
                    
                    existing_users = User.objects.exclude(id=user.id).filter(face_encoding__isnull=False)
                    for existing_user in existing_users:
                        existing_face_encoding = existing_user.get_face_encoding()
                        if compare_faces(existing_face_encoding, face_encoding):
                            messages.error(request, "มีใบหน้านี้อยู่ในระบบอยู่แล้ว")
                            return render(request, "register.html")
                    
                    # Save face encoding and activate user
                    user.face_encoding = face_encoding
                    user.is_active = True
                    user.save()

                    # Log the user in after registration
                    backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user, backend=backend)

                    # Clean up session after successful registration
                    if 'otp_verification' in request.session:
                        del request.session['otp_verification']

                    messages.success(request, "ลงทะเบียนเสร็จสิ้นคุณกำลังเข้าสู่ระบบ")
                    return redirect("index")
                else:
                    messages.error(request, image_processing_outcome.get('error'))
                    return render(request, "register.html")
        
        else:
            # This is the first time the user submits the form (before OTP verification)
            if email:
                # Generate and send OTP
                otp = generate_otp()
                print(f"Debug OTP {otp}")
                otp_sent = send_otp_email_helper(email, otp)

                if otp_sent:
                    # Store OTP in session for verification
                    request.session['otp_verification'] = {
                        'sid': sid,
                        'name': name,
                        'last_name': last_name,
                        'branch': branch,
                        'email': email,
                        'otp': otp
                    }

                    messages.info(request, "ระบบได้ส่ง OTP ไปแล้ว")
                    return render(request, "register.html", {
                        "sid": sid,
                        "name": name,
                        "last_name": last_name,
                        "branch": branch,
                        "email": email
                    })
                else:
                    messages.error(request, "ไม่สามารถส่ง OTP ได้โปรดลองใหม่อีกครั้งในภายหลัง")
                    return render(request, "register.html")
            else:
                messages.error(request, "กรุณากรอก email เพื่อส่ง OTP")
                return render(request, "register.html")

    return render(request, "register.html")


def process_user_image(captured_image_base64):
    try:
        format, imgstr = captured_image_base64.split(";base64,")  # Split format and data
        image_data = base64.b64decode(imgstr)
        image = Image.open(BytesIO(image_data))
        if image.mode != "RGB":
            image = image.convert("RGB")

        image_np = np.array(image)  # Convert image to numpy array for face_recognition
        face_encodings = face_recognition.face_encodings(image_np)
        if face_encodings:
            return {'success': True, 'face_encoding': face_encodings[0].tolist()}
        else:
            return {'success': False, 'error': "ไม่มีหน้าปรากฎบนภาพโปรดถ่ายภาพใหม่อีกครั้ง"}
    except Exception as e:
        return {'success': False, 'error': str(e)}





def facial_login(request):
    if request.method == "POST":
        captured_image_base64 = request.POST.get("image")

        if captured_image_base64:
            # Decode the base64 image
            format, imgstr = captured_image_base64.split(";base64,")
            image_data = base64.b64decode(imgstr)

            # Convert the image data to an image object using PIL
            image = Image.open(BytesIO(image_data))

            # Ensure the image is in RGB mode (required by face_recognition)
            if image.mode != "RGB":
                image = image.convert("RGB")

            image_np = np.array(image)  # Convert image to numpy array

            # Extract face encoding from the captured image
            captured_face_encodings = face_recognition.face_encodings(image_np)

            if captured_face_encodings:
                captured_face_encoding = captured_face_encodings[0]

                # Compare captured face encoding with known face encodings in the database
                for user in User.objects.all():
                    if user.face_encoding:  # Ensure face_encoding is not None
                        known_face_encoding = json.loads(
                            user.face_encoding
                        )  # Load face encoding from JSON
                        results = face_recognition.compare_faces(
                            [known_face_encoding], captured_face_encoding
                        )

                        if results[0]:  # Face match found
                            backend = 'django.contrib.auth.backends.ModelBackend'
                            login(request, user, backend=backend)  # Log the user in
                            messages.success(request, "เข้าสู่ระบบเสร็จสิ้น")  # Success message
                            return redirect("index")  # Replace 'index' with your desired view name

            messages.error(request, "ไม่พบใบหน้าของคุณโปรดลองใหม่อีกครั้ง")  # Error message if no match found
            return render(request, "facial_login.html")

    return render(request, "facial_login.html")
