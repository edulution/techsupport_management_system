from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import UserProfile, SupportTicket
from .serializers import (
    ProfileSerializer,
    TicketDetailsSerializer,
    CreateTicketSerializer,
    AllTicketsSerializer,
    OpenTicketsSerializer,
    ResolvedTicketsSerializer,
    InProgressTicketsSerializer,
)

""" API view to retrieve the profile of the authenticated user """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_api(request):
    user = request.user
    try:
        # Retrieve the user's profile and serialize it
        profile = user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Return a 404 response if the user's profile is not found
        return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

"""API view to retrieve details of a specific support ticket by ID """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_details_api(request, ticket_id):
    # Retrieve the support ticket by ID and serialize it
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    serializer = TicketDetailsSerializer(ticket)
    return Response(serializer.data)

""" API view to create a new support ticket """
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ticket_api(request):
    # Validate the input data and save the new support ticket
    serializer = CreateTicketSerializer(data=request.data, context={'user': request.user})
    if serializer.is_valid():
        serializer.save(submitted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

""" API view to retrieve all support tickets based on user role """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_tickets_api(request):
    user = request.user
    context = {}

    if user.is_user():
        # If the user is a regular user, retrieve their submitted tickets and center tickets
        user_tickets = user.submitted_issues.all()
        center = user.centres.first()
        centre_tickets = SupportTicket.objects.filter(centre=center)
        user_and_centre_tickets = user_tickets | centre_tickets
    elif user.is_technician():
        # If the user is a technician, retrieve tickets assigned to them and submitted by them
        user_and_centre_tickets = SupportTicket.objects.filter(assigned_to=user, submitted_by=user)
    elif user.is_manager() or user.is_admin():
        # If the user is a manager or admin, retrieve tickets submitted by them
        user_and_centre_tickets = SupportTicket.objects.filter(submitted_by=user)
    else:
        user_and_centre_tickets = None

    # Serialize the retrieved tickets
    serializer = AllTicketsSerializer(user_and_centre_tickets, many=True)
    return Response(serializer.data)

""" API view to retrieve open support tickets """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def open_tickets_api(request):
    # Retrieve and serialize open support tickets
    tickets = SupportTicket.objects.filter(status="Open")
    serializer = OpenTicketsSerializer(tickets, many=True)
    return Response(serializer.data)

""" API view to retrieve resolved support tickets """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resolved_tickets_api(request):
    # Retrieve and serialize resolved support tickets
    tickets = SupportTicket.objects.filter(status="Resolved")
    serializer = ResolvedTicketsSerializer(tickets, many=True)
    return Response(serializer.data)

""" API view to retrieve support tickets in progress """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tickets_in_progress_api(request):
    # Retrieve and serialize support tickets in progress
    tickets = SupportTicket.objects.filter(status="In Progress")
    serializer = InProgressTicketsSerializer(tickets, many=True)
    return Response(serializer.data)