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
    


from .models import Users

class UserOnBoardingSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type':'password'})

    class Meta:
        model = Users
        fields = ['username','name','email', 'password','role']
        extra_kwargs={
            'password':{'write_only':True},
            'role':{'read_only':True}
        }

    def create(self, validated_data):
        user = Users.objects.create_user(
            username=validated_data['email'], 
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name'),
            role='employee' # Force default role for security
        )
        return user