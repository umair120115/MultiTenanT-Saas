from rest_framework import serializers
from .models import Lead
from accounts.models import Users




# class LeadSerializer(serializers.ModelSerializer):

class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for the Handler"""
    class Meta:
        model = Users
        fields = ['id', 'username', 'email']



class LeadSerializer(serializers.ModelSerializer):
    # Nested serializers for Efficient Reading (GET)
    handler_details = UserSummarySerializer(source='handler', read_only=True)
    # notes = LeadNoteSerializer(source='update_notes', many=True, read_only=True)
    
    # We keep the original fields for Writing (POST)
    handler = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(), 
        required=False
    )

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'source', 'status', 'value', 
            'expected_closure_date', 'description', 
            'handler', 'handler_details', # Write ID, Read Details
            # 'company', 
            # 'notes', # The Many-to-Many list
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Optional: Auto-assign the logged-in user if no handler is provided
        request = self.context.get('request')
        if request and hasattr(request, 'user') and not validated_data.get('handler'):
            validated_data['handler'] = request.user
        return super().create(validated_data)
from .models import UpdateLeadNotes    
class LeadUpdateNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateLeadNotes
        fields = ['lead','note','created_at']

from rest_framework import serializers
from .models import Lead, UpdateLeadNotes

# 1. Ensure this serializer is defined first or imported
class LeadUpdateNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateLeadNotes
        fields = ['id', 'note', 'created_at'] # Added 'id' for good practice

class LeadDetailSerializer(serializers.ModelSerializer):
    handler_details = UserSummarySerializer(source='handler', read_only=True)
    
    # 2. Change this to SerializerMethodField to enable custom sorting
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'name', 'source', 'status', 'value',
            'expected_closure_date', 'description',
            'handler_details', 'notes'
        ]

    # 3. Implement the logic to fetch, sort, and serialize
    def get_notes(self, obj):
        # Fetch the related notes using the related_name 'update_notes_leads'
        notes_qs = obj.update_notes_leads.all().order_by('-created_at')
        
        # Manually invoke the serializer on the sorted queryset
        return LeadUpdateNotesSerializer(notes_qs, many=True).data