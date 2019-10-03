from rest_framework import serializers
from .models import Contact
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.conf import settings
import jwt, calendar


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'mobile', 'telephone', 'address')

    def create(self, validated_data):
        print(validated_data)
        contact = Contact.objects.create(**validated_data)
        print(contact)
        return contact


class ProfileSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(
        min_length=8,
        max_length=15,
        write_only=True
    )
    old_password = serializers.CharField(
        min_length=8,
        max_length=15,
        write_only=True
    )
    name = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'confirm', 'old_password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 15}}

    def validate_email(self, value):
        """
        Check email address uniqueness.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address must be uniqueness.")
        return value

    def validate_old_password(self, value):
        if self.instance.check_password(value):
            return value
        raise serializers.ValidationError('Invalid password.')

    def validate(self, data):
        if data["password"] != data["confirm"]:
            raise serializers.ValidationError("Not matched password.")
        data['name'] = data.pop('first_name')
        return data

    def update(self, instance, validated_data):
        data = validated_data
        data['first_name'] = data.pop('name')
        data['username'] = data['email'].split('@')[0]
        data.pop('confirm')
        password = data.pop('password')
        instance.email = data.get('email', None)
        instance.first_name = data.get('first_name', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    confirm = serializers.CharField(
        min_length=8,
        max_length=15,
        write_only=True
    )
    contacts_url = serializers.HyperlinkedIdentityField(
        view_name='contacts',
        lookup_field='id'
    )
    name = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'confirm', 'contacts_url')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8, 'max_length': 15}}

    def validate_email(self, value):
        """
        Check email address uniqueness.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address must be uniqueness.")
        return value

    def validate(self, data):
        if data["password"] != data["confirm"]:
            raise serializers.ValidationError("Not matched password.")
        data['name'] = data.pop('first_name')
        return data

    def create(self, validated_data):
        data = validated_data
        data['first_name'] = data.pop('name')
        data['username'] = data['email'].split('@')[0]
        data.pop('confirm')
        pasword = data.pop('password')
        user = User(**data)
        user.set_password(pasword)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        max_length=15,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    def _generate_jwt_token(self, email):
        dt = datetime.now() + timedelta(days=1)
        token = jwt.encode({
            'email': email,
            'exp': calendar.timegm(dt.utctimetuple())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')

    def _get_or_none(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        user = self._get_or_none(email)
        if user and user.check_password(password):
            token = self._generate_jwt_token(email)
        else:
            raise serializers.ValidationError('Username or password is incorrect.')
        return {"token": token, "email": email}