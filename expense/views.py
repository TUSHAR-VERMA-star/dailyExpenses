import csv
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import User, Expense
from .serializers import UserSerializer, ExpenseSerializer

# API view to handle User creation and retrieval
class UserAPIView(APIView):
    def get(self, request, user_id=None):
        """
        Retrieve user details if user_id is provided.
        If no user_id is provided, retrieve all users.
        """
        if user_id:
            user = get_object_or_404(User, id=user_id)
            serializer = UserSerializer(user)
        else:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new user.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API view to handle retrieval of individual user's expenses
class UserExpensesAPIView(APIView):
    def get(self, request, user_id):
        """
        Retrieve expenses for a specific user identified by user_id.
        """
        user = get_object_or_404(User, id=user_id)
        expenses = Expense.objects.filter(user=user).select_related('user')
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API view to handle adding an expense
class AddExpenseAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        """
        Add a new expense and split it among participants based on the chosen split method.
        """
        data = request.data
        split_method = data.get("split_method")
        participants = data.get("participants")

        # Validate and save the expense data
        expense_serializer = ExpenseSerializer(data=data)
        expense_serializer.is_valid(raise_exception=True)
        expense = expense_serializer.save()

        # Split the expense based on the chosen method
        if split_method == "equal":
            self.split_equal(expense, participants)
        elif split_method == "exact":
            self.split_exact(expense, participants)
        elif split_method == "percentage":
            self.split_percentage(expense, participants)
        else:
            return Response({"error": "Invalid split method"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(expense_serializer.data, status=status.HTTP_201_CREATED)

    def split_equal(self, expense, participants):
        """
        Split the expense equally among all participants.
        """
        total_amount = expense.amount
        num_participants = len(participants)
        if num_participants == 0:
            raise ValidationError("Participants are required for equal split method")
        split_amount = total_amount / num_participants

        for participant in participants:
            user = get_object_or_404(User, id=participant['user_id'])
            Expense.objects.create(
                user=user,
                description=f"Split of {expense.description}",
                amount=split_amount,
                split_method="equal",
                date_created=expense.date_created
            )

    def split_exact(self, expense, participants):
        """
        Split the expense with exact amounts for each participant.
        """
        total_amount = sum(participant['amount'] for participant in participants)
        if total_amount != expense.amount:
            raise ValidationError("Total split amounts must equal the expense amount")

        for participant in participants:
            user = get_object_or_404(User, id=participant['user_id'])
            amount = participant['amount']
            Expense.objects.create(
                user=user,
                description=f"Split of {expense.description}",
                amount=amount,
                split_method="exact",
                date_created=expense.date_created
            )

    def split_percentage(self, expense, participants):
        """
        Split the expense based on percentages.
        """
        total_amount = expense.amount
        total_percentage = sum(participant['percentage'] for participant in participants)

        if total_percentage != 100:
            raise ValidationError("Total percentage must be 100%")

        for participant in participants:
            user = get_object_or_404(User, id=participant['user_id'])
            percentage = participant['percentage']
            amount = total_amount * (percentage / 100)
            Expense.objects.create(
                user=user,
                description=f"Split of {expense.description}",
                amount=amount,
                split_method="percentage",
                date_created=expense.date_created
            )

# API view to handle retrieval of all expenses
class OverallExpensesAPIView(APIView):
    def get(self, request):
        """
        Retrieve all expenses.
        """
        expenses = Expense.objects.all().select_related('user')
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API view to handle downloading the balance sheet
class DownloadBalanceSheetAPIView(APIView):
    def get(self, request):
        """
        Create and return a CSV file of all expenses.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Description', 'Amount', 'Split Method', 'Date Created'])

        expenses = Expense.objects.all().select_related('user')
        for expense in expenses:
            writer.writerow([expense.user.name, expense.description, expense.amount, expense.split_method, expense.date_created])

        return response
