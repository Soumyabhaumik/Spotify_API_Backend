import json
from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from supabase import create_client, Client
from django.contrib import messages
import logging
from django.core.handlers.wsgi import WSGIRequest

logger = logging.getLogger(__name__)

# Supabase client setup
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

request: WSGIRequest


def google_callback(request):
    print(type(request))
    """
    Handles the callback from Google OAuth.
    """
    # Debug: See what data comes back from Google
    # Get the code from the query parameters

    print("Request ______", request)
    print(
        "###############################################Request GET:",
        request.GET["code"],
        # .get("code")[0],
    )
    # Debug: See what data comes back from Google

    code = request.GET.get("code")
    # code = request.GET["code"]
    print(code)
    if not code:
        error_message = "Authorization code not provided."
        logger.error(error_message)
        messages.error(request, error_message)
        return redirect("auth:login")

    try:
        # Exchange the code for a session. This is the corrected method call.
        print("hiuchwiuchviuvhiuwhviowhi")
        au_code = {"auth_code": str(code)}
        print("au_code", au_code)
        response = supabase.auth.exchange_code_for_session(au_code)
        print("Response", response)
        # Now we can get the session and user
        session = response.session
        print("Session", session)
        user = response.user

        if session:
            # Store session data in Django's session
            request.session["user"] = user.email
            request.session["jwt"] = session.access_token
            metadata = user.user_metadata
            # if isinstance(metadata, str):
            #     try:
            #         metadata = json.loads(metadata)
            #     except json.JSONDecodeError:
            #         metadata = {}
            # elif not isinstance(metadata, dict):
            #     metadata = {}

            name = metadata.get("name", "")

            request.session["name"] = name
            request.session.save()
            messages.success(request, "Successfully logged in with Google!")
            return redirect("auth:home")
        else:
            error_message = "Failed to retrieve session after exchanging code."
            logger.error(error_message)
            messages.error(request, error_message)
            return redirect("auth:login")

    except Exception as e:
        error_message = f"Error during code exchange: {str(e)}"
        logger.error(error_message)
        messages.error(request, error_message)
        return redirect("auth:login")


@csrf_exempt
def google_login(request):
    """
    Initiates the Google OAuth flow.
    """
    # Construct the redirect URL.  Crucially, use Django's reverse() to get the full URL.
    # redirect_to = request.build_absolute_uri(
    #     reverse("auth:google_callback")
    # )  # Ensure this matches your URL pattern name
    redirect_to = "http://127.0.0.1:8000/google_callback/"
    print("redirect_to_google_login", redirect_to)
    try:
        response = supabase.auth.sign_in_with_oauth(
            {
                "provider": "google",
                "options": {
                    "redirect_to": redirect_to,
                },
            }
        )

        # The response now contains a URL to redirect the user to.
        # We should not try to access .user or .session.  Those will be None.
        print("google_login_response_", response)  # useful for debugging
        return redirect(response.url)  # Redirect the user to Google
    except Exception as e:
        error_message = f"Google OAuth error: {str(e)}"
        logger.error(error_message)
        messages.error(request, error_message)
        return redirect("auth:login")  # Redirect to login page on error


# def google_callback(request):
#     """
#     Handles the callback from Google OAuth.
#     """
#     # Debug: See what data comes back from Google
#     # Get the code from the query parameters

#     print
#     ("Request Method:", request.method)
#     # Debug: Check the request method

#     print
#     ("Request GET:", request.GET)
#     # Debug: See what data comes back from Google

#     print
#     ("Request Body:", request.body)
#     code = request.GET.get("code")
#     if not code:
#         error_message = "Authorization code not provided."
#         logger.error(error_message)
#         messages.error(request, error_message)
#         return redirect("auth:login")

#     try:
#         # Exchange the code for a session. This is the corrected method call.
#         response = supabase.auth.exchange_code_for_session(code)

#         # Now we can get the session and user
#         session = response.session
#         print(session)
#         user = response.user

#         if session:
#             # Store session data in Django's session
#             request.session["user"] = user.email
#             request.session["jwt"] = session.access_token
#             # metadata = user.user_metadata
#             # if isinstance(metadata, str):
#             #     try:
#             #         metadata = json.loads(metadata)
#             #     except json.JSONDecodeError:
#             #         metadata = {}
#             # elif not isinstance(metadata, dict):
#             #     metadata = {}

#             # name = metadata.get("name", "")
#             name = "dkjbsbvisrv"
#             request.session["name"] = name
#             request.session.save()
#             messages.success(request, "Successfully logged in with Google!")
#             return redirect("auth:home")
#         else:
#             error_message = "Failed to retrieve session after exchanging code."
#             logger.error(error_message)
#             messages.error(request, error_message)
#             return redirect("auth:login")

#     except Exception as e:
#         error_message = f"Error during code exchange: {str(e)}"
#         logger.error(error_message)
#         messages.error(request, error_message)
#         return redirect("auth:login")


@csrf_exempt
def login_view(request):
    """
    Handles user login, both for standard web requests and JSON API requests.
    """
    if request.method == "POST":
        is_json = request.content_type == "application/json"

        # Extract email and password
        try:
            if is_json:
                data = json.loads(request.body)
                email = data.get("email")
                password = data.get("password")
            else:
                email = request.POST.get("email")
                password = request.POST.get("password")
        except Exception as e:
            logger.error(f"Error extracting data: {e}")
            return JsonResponse({"error": "Invalid request data"}, status=400)

        # Input validation
        if not email or not password:
            error_message = "Email and password are required."
            logger.warning(error_message)
            if is_json:
                return JsonResponse({"error": error_message}, status=400)
            return render(request, "login.html", {"error": error_message})

        try:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
            session = response.session
            user = response.user

            if session:
                # Store session data
                request.session["user"] = user.email
                request.session["jwt"] = session.access_token
                name = user.user_metadata.get("name", "")
                request.session["name"] = name
                request.session.save()  # Ensure session is saved

                if is_json:
                    return JsonResponse(
                        {
                            "message": "Login successful",
                            "email": user.email,
                            "name": name,
                            "jwt": session.access_token,
                            "refresh_token": session.refresh_token,
                            "sessionid": request.session.session_key,
                        }
                    )
                return redirect("auth:home")  # Use the named URL

            else:
                error_message = "Invalid credentials"
                logger.warning(error_message)
                if is_json:
                    return JsonResponse({"error": error_message}, status=401)
                return render(request, "login.html", {"error": error_message})

        except Exception as e:
            error_message = f"Login error: {str(e)}"
            logger.error(error_message)
            if is_json:
                return JsonResponse({"error": error_message}, status=400)
            return render(request, "login.html", {"error": error_message})

    # GET method
    return render(request, "login.html")


@csrf_exempt
def signup_view(request):
    """Handles user signup, supporting both JSON and form data."""
    if request.method == "POST":
        is_json = request.content_type == "application/json"

        try:
            if is_json:
                data = json.loads(request.body)
                name = data.get("name")
                email = data.get("email")
                password = data.get("password")
            else:
                name = request.POST.get("name")
                email = request.POST.get("email")
                password = request.POST.get("password")
        except json.JSONDecodeError:
            error_message = "Invalid JSON" if is_json else "Invalid form data"
            logger.error(error_message)
            return JsonResponse({"error": error_message}, status=400)

        # Input validation
        if not name or not email or not password:
            error_message = "Name, email, and password are required."
            logger.warning(error_message)
            if is_json:
                return JsonResponse({"error": error_message}, status=400)
            return render(request, "signup.html", {"error": error_message})

        try:
            response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"name": name}},
                }
            )
            if is_json:
                return JsonResponse(
                    {"message": "Signup successful. Please log in."}, status=201
                )
            messages.success(request, "Signup successful. Please log in.")
            return redirect("auth:login")  # Use named URL

        except Exception as e:
            error_message = f"Signup error: {str(e)}"
            logger.error(error_message)
            if is_json:
                return JsonResponse({"error": error_message}, status=400)
            return render(request, "signup.html", {"error": error_message})

    return render(request, "signup.html")


def home_view(request):
    """
    Handles the home view, ensuring the user is authenticated via session.
    Supports both JSON and HTML responses.
    """
    user_email = request.session.get("user")
    if not user_email:
        error_message = "Unauthorized"
        logger.warning(error_message)
        if (
            request.content_type == "application/json"
            or request.headers.get("Accept") == "application/json"
        ):
            return JsonResponse({"error": error_message}, status=401)
        return redirect("auth:login")  # Use named URL

    name = request.session.get("name", "")
    if (
        request.content_type == "application/json"
        or request.headers.get("Accept") == "application/json"
    ):
        return JsonResponse(
            {
                "message": "Welcome to the Home page! User is authenticated",
                "email": user_email,
                "name": name,
            }
        )

    return render(request, "home.html", {"user_email": user_email, "name": name})


@csrf_exempt
def logout_view(request):
    """
    Handles user logout, clearing the session.  Supports JSON and HTML.
    """
    user_email = request.session.get("user", "User")  # Get user *before* flush
    logger.info(f"User {user_email} logged out.")

    # Clear session data
    request.session.flush()

    if (
        request.content_type == "application/json"
        or request.headers.get("Accept") == "application/json"
    ):
        return JsonResponse({"message": f"{user_email} is successfully logged out"})

    return redirect("auth:login")  # Use named URL
