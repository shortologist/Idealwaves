from django.contrib.auth.models import User as userModel
from rest_framework import views, response, status
from .serializers import UserSerializer, LoginSerializer, ContactSerializer, ProfileSerializer
from .models import Contact


class HomeView(views.APIView):
    def get(self, request):
        users = userModel.objects.all()
        serializer = UserSerializer(users, many=True, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class RegisterView(views.APIView):

    def post(self, request):
        user = UserSerializer(data=request.data, context={"request": request})
        if user.is_valid():
            user.save()
            return response.Response(user.data, status=status.HTTP_201_CREATED)
        return response.Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactsView(views.APIView):

    def get(self, request, id):
        user = userModel.objects.get(pk=id)
        serializer = ContactSerializer(user.contacts, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id):
        if request.user:
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)


class ContactView(views.APIView):

     def get(self, request, id, pk):
         user = userModel.objects.get(pk=id)
         contact = user.contacts.get(pk=pk)
         serializer = ContactSerializer(contact)
         return response.Response(serializer.data, status=status.HTTP_200_OK)

     def put(self, request, id, pk):
         contact = Contact.objects.get(pk=pk)
         serializer = ContactSerializer(contact, data=request.data)
         if serializer.is_valid():
             serializer.save()
             return response.Response(serializer.data, status=status.HTTP_200_OK)
         return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

     def delete(self, request, id, pk):
         contact = Contact.objects.get(pk=pk)
         contact.delete()
         return response.Response(status=status.HTTP_200_OK)


class ProfileView(views.APIView):

    def get(self, request):
        if request.user:
            serializer = ProfileSerializer(request.user)
            return response.Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.user:
            serializer = ProfileSerializer(request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)