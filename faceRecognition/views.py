import face_recognition
import base64
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import CustomUser
import random
import string
from io import BytesIO
from PIL import Image
import numpy as np
import json
from django.contrib.auth.decorators import user_passes_test


def staff_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_staff)(view_func)
    return decorated_view_func


def generate_random_password():
    """Generate a random password for the user."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))


@staff_required
def register(request):
    if request.method == "POST":
        sid = request.POST.get("sid")
        captured_image_base64 = request.POST.get("image")

        # Check if the SID already exists
        if CustomUser.objects.filter(sid=sid).exists():
            return render(
                request,
                "register.html",
                {"error": "Sid already exists. Please choose a different Sid."},
            )

        if sid and captured_image_base64:
            # Create the user with a random password
            password = generate_random_password()
            user = CustomUser.objects.create(sid=sid)
            user.set_password(password)  # Set the random password
            user.save()

            # Decode the base64 image
            format, imgstr = captured_image_base64.split(
                ";base64,"
            )  # Split the format and data
            image_data = base64.b64decode(imgstr)

            # Convert the image data to an image object using PIL
            image = Image.open(BytesIO(image_data))

            # Ensure the image is in RGB mode (required by face_recognition)
            if image.mode != "RGB":
                image = image.convert("RGB")

            image_np = np.array(
                image
            )  # Convert image to a numpy array for face_recognition

            # Extract face encodings using face_recognition
            face_encodings = face_recognition.face_encodings(image_np)

            if face_encodings:  # Check if any face encodings were detected
                face_encoding = face_encodings[0].tolist()  # Convert ndarray to list
                # Save face encoding directly in CustomUser
                user.set_face_encoding(face_encoding)
                user.save()

                # Automatically log the user in after registration
                login(request, user)
                return redirect("index")
            else:
                return render(
                    request,
                    "register.html",
                    {"error": "No face detected in the image. Please try again."},
                )
        else:
            return render(
                request,
                "register.html",
                {"error": "Please fill in the sid and capture a face."},
            )

    return render(request, "register.html")


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
                for user in CustomUser.objects.all():
                    if user.face_encoding:  # Ensure face_encoding is not None
                        known_face_encoding = json.loads(
                            user.face_encoding
                        )  # Load face encoding from JSON
                        results = face_recognition.compare_faces(
                            [known_face_encoding], captured_face_encoding
                        )

                        if results[0]:  # Face match found
                            login(request, user)  # Log the user in
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
