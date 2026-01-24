from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Proficient Design: Customize the JWT response to include user details.
    This saves an extra API call on the frontend.
    """
    def validate(self, attrs):
        # 1. Let the parent class validate credentials and create tokens
        data = super().validate(attrs)

        # 2. 'self.user' is available after validation. 
        # Inject custom data into the response dictionary.
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'name': self.user.get_full_name() or self.user.username,
            # Ensure your User model has a 'role' field, or use a method
            'role': getattr(self.user, 'role', 'USER'), 
        }

        return data