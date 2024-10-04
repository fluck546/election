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

def register(request):
    if request.method == "POST":
        # Retrieve data from form
        sid = request.POST.get("sid")
        name = request.POST.get("name")
        last_name = request.POST.get("last_name")
        branch = request.POST.get("branch")
        captured_image_base64 = request.POST.get("image")

        # Check if the user exists with the given SID and other fields but is not yet active
        user = User.objects.filter(sid=sid, name=name, last_name=last_name, branch=branch, is_active=False).first()
        
        if not user:
            return render(
                request,
                "register.html",
                {"error": "No matching inactive user found or you have already been activated. Please check your details or contact support."},
            )

        if captured_image_base64:
            # Process the image and extract face encoding
            image_processing_outcome = process_user_image(captured_image_base64)
            if image_processing_outcome.get('success'):
                face_encoding = image_processing_outcome.get('face_encoding')
                
                existing_users = User.objects.exclude(id=user.id).filter(face_encoding__isnull=False)
                for existing_user in existing_users:
                    existing_face_encoding = existing_user.get_face_encoding()  # Ensure you have a method to get the encoding from JSON
                    if compare_faces(existing_face_encoding, face_encoding):
                        return render(request, "register.html", {"error": "This face is already registered to another user."})
                
                
                
                user.face_encoding = face_encoding
                user.is_active = True  # Activate the user
                user.save()

                # Log the user in after registration
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend = backend)
                return redirect("index")
            else:
                return render(request, "register.html", {"error": image_processing_outcome.get('error')})

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
            return {'success': False, 'error': "No face detected in the image. Please try again."}
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
                            login(request, user, backend = backend)  # Log the user in
                            return redirect(
                                "index"
                            )  # Replace 'dashboard' with your desired view name

        # If no match is found, return an error message
        return render(
            request,
            "facial_login.html",
            {"error": "Face not recognized. Please try again."},
        )

    return render(request, "facial_login.html")
