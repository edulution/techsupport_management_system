from rest_framework import serializers
from .models import SupportTicket, UserProfile

class CreateSupportTicketSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new SupportTicket instance.
    """
    class Meta:
        model = SupportTicket
        fields = [
            'title',
            'category',
            'subcategory',
            'priority',
            'centre',
            'description',
        ]

    def create(self, validated_data):
        """
        Custom create method to associate the user with the support ticket.
        """
        # Extracting the user from the request context
        user = self.context['request'].user
        validated_data['submitted_by'] = user

        # Creating and returning the support ticket
        return SupportTicket.objects.create(**validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    class Meta:
        model = UserProfile
        fields = '__all__'

class TicketDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of a SupportTicket.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'

class CreateTicketSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new SupportTicket instance.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'

class AllTicketsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of all SupportTicket instances.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'

class OpenTicketsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of open SupportTicket instances.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'

class ResolvedTicketsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of resolved SupportTicket instances.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'

class InProgressTicketsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying details of in-progress SupportTicket instances.
    """
    class Meta:
        model = SupportTicket
        fields = '__all__'
