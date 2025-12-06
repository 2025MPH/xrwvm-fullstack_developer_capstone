from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime

import logging
import json
from django.views.decorators.csrf import csrf_exempt

from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request body (sent as JSON)
    data = json.loads(request.body)
    username = data.get("userName")
    password = data.get("password")

    # Try to check if provided credentials can be authenticated
    user = authenticate(username=username, password=password)
    resp = {"userName": username}

    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        resp["status"] = "Authenticated"

    return JsonResponse(resp)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)  # Terminate user session
    data = {"userName": ""}  # Return empty username
    return JsonResponse(data)


# get_cars
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})


# Update the `get_dealerships` view to return a list of dealerships as JSON
def get_dealerships(request, state="All"):
    """
    Return dealerships, optionally filtered by state, as JSON for the React frontend.
    React's Dealers.jsx expects:
        { "status": 200, "dealers": [ ... ] }
    """
    if request.method != "GET":
        return JsonResponse(
            {"status": 405, "message": "Method not allowed"}, status=405
        )

    # Build the backend endpoint for the Node/Mongo service
    if state and state != "All":
        endpoint = f"/fetchDealers/{state}"
    else:
        endpoint = "/fetchDealers"

    try:
        dealerships = get_request(endpoint)
        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        logger.error(f"Error fetching dealers: {e}")
        return JsonResponse(
            {"status": 500, "message": "Error fetching dealers"}, status=500
        )


# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)

        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail["review"])
            print(response)

            # ✅ FIXED: Prevent crash if sentiment API returns None
            sentiment = (
                response.get("sentiment")
                if response and isinstance(response, dict)
                else "neutral"
            )
            review_detail["sentiment"] = sentiment

        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create an `add_review` view to submit a review
def add_review(request):
    if request.user.is_anonymous is False:
        data = json.loads(request.body)
        try:
            _ = post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
