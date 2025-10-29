from allauth.account.forms import SignupForm

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        # Тук можеш да добавиш логика за потребителя след регистрация, ако искаш
        return user