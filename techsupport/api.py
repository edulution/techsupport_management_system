from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SupportTicket, UserProfile
from .serializers import SupportTicketSerializer, UserProfileSerializer

# API for creating a support ticket
class CreateTicketAPIView(APIView):
    def post(self, request):
        # Validate and save the support ticket
        serializer = SupportTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API for retrieving details of a specific support ticket
class TicketDetailsAPIView(APIView):
    def get(self, request, ticket_id):
        # Retrieve and serialize the support ticket
        ticket = SupportTicket.objects.get(id=ticket_id)
        serializer = SupportTicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API for retrieving the profile of the currently authenticated user
class ProfileAPIView(APIView):
    def get(self, request):
        # Retrieve and serialize the user profile
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API for retrieving all support tickets
class AllTicketsAPIView(APIView):
    def get(self, request):
        # Retrieve and serialize all support tickets
        tickets = SupportTicket.objects.all()
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API for retrieving open support tickets
class OpenTicketsAPIView(APIView):
    def get(self, request):
        # Retrieve and serialize open support tickets
        tickets = SupportTicket.objects.filter(status="Open")
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API for retrieving resolved support tickets
class ResolvedTicketsAPIView(APIView):
    def get(self, request):
        # Retrieve and serialize resolved support tickets
        tickets = SupportTicket.objects.filter(status="Resolved")
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API for retrieving support tickets in progress
class TicketsInProgressAPIView(APIView):
    def get(self, request):
        # Retrieve and serialize support tickets in progress
        tickets = SupportTicket.objects.filter(status="In Progress")
        serializer = SupportTicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
