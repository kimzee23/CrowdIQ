from domain.model.user import User


class LoginValidator:
    @staticmethod
    def validate_login_request(user: User) -> None:
        if not user.is_active:
            raise ValueError("User is not active")
        if not user.is_verified:
            raise ValueError("Invalid credentials. Please verify .")
