import face_recognition
import base64
from django.core.files.base import ContentFile
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .form import UserRegistrationForm
from .models import UserProfile
from django.db import transaction, IntegrityError
import numpy as np
from django.contrib import messages
from django.db.models.signals import post_save
from .signal import create_or_update_user_profile  # Import your signal handler
import json
import binascii

def register_user(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            image_data = request.POST.get('image')
            if image_data:
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')

                    # Load image and extract face encoding
                    face_image = face_recognition.load_image_file(image)
                    face_encoding = face_recognition.face_encodings(face_image)

                    if len(face_encoding) > 0:
                        with transaction.atomic():
                            face_encoding = face_encoding[0]
                            print("Extracted face encoding:", face_encoding)

                            # Temporarily disconnect the post_save signal
                            post_save.disconnect(create_or_update_user_profile, sender=User)

                            # Create the User object
                            user = form.save()

                            # Now create the UserProfile
                            profile = UserProfile.objects.create(user=user, username=user.username, face_encoding=face_encoding.tobytes())

                            # Reconnect the signal
                            post_save.connect(create_or_update_user_profile, sender=User)

                        # Automatically log in the user and redirect
                        login(request, user)
                        messages.success(request, "Registration successful! You are now logged in.")
                        return redirect('login')

                    else:
                        print("No face detected in the image.")
                        return render(request, 'register.html', {'form': form, 'error': 'No face detected. Please try again.'})

                except (IOError, ValueError) as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error during registration: {e}")
                    return render(request, 'register.html', {'form': form, 'error': 'An error occurred during registration. Please try again.'})

            else:
                return render(request, 'register.html', {'form': form, 'error': 'Please upload an image.'})

        else:
            return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


def facial_login(request):
    if request.method == 'POST':
        image_data = request.POST.get('image') 

        if image_data:
            try:
                print("Received image data:", image_data[:50])  # Debugging: Print a snippet of the image data

                # Directly split the image_data string 
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                try:
                    image = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
                except binascii.Error as e:
                    return render(request, 'facial_login.html', {'error': f'Error decoding image data: {e}'})

                unknown_image = face_recognition.load_image_file(image)
                print("Loaded unknown image:", unknown_image)  # Debugging: Check if image loaded correctly

                unknown_encoding = face_recognition.face_encodings(unknown_image)
                print("Unknown encodings:", unknown_encoding)  # Debugging: Check if encodings were extracted

                if len(unknown_encoding) > 0:
                    unknown_encoding = unknown_encoding[0]

                    for user in User.objects.all():
                        try:
                            profile = UserProfile.objects.get(user=user) 
                            known_encoding_bytes = profile.face_encoding

                            if known_encoding_bytes:
                                print("Retrieved face encoding (bytes):", known_encoding_bytes)  # Debugging
                                print("Size of known_encoding_bytes:", len(known_encoding_bytes))  # Debugging

                                # Explicitly check and convert to bytes if needed
                                if isinstance(known_encoding_bytes, str):
                                    known_encoding_bytes = known_encoding_bytes.encode('utf-8')

                                known_encoding = np.frombuffer(known_encoding_bytes, dtype=np.float64)  
                                matches = face_recognition.compare_faces([known_encoding], unknown_encoding)
                                if matches[0]:
                                    login(request, user)
                                    return redirect('vote', round_id=4) 
                        except UserProfile.DoesNotExist:
                            # Handle the case where UserProfile doesn't exist for this user
                            print(f"No UserProfile found for user: {user.username}")
                            continue  

                return render(request, 'facial_login.html', {'error': 'Face not recognized'})

            except ValueError as e:
                return render(request, 'facial_login.html', {'error': f'Invalid image data: {e}'})
        else:
            return render(request, 'facial_login.html', {'error': 'No image data provided'})

    return render(request, 'facial_login.html')