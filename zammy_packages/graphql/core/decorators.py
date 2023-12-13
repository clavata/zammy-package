from zammy_packages.graphql.core.authentication import CognitoAuthentication
from zammy_packages.account.models import ZammyAccount


def cognito_authenticaion(func):
    def wrapper(*info, **kwargs):
        claims = CognitoAuthentication.verify_to_cognito_id_token(info[1])
        try:
            user = ZammyAccount.objects.get(email=claims["email"])
        except ZammyAccount.DoesNotExist:
            raise Exception("해당 유저는 존재하지 않습니다.")
        return func(user, *info, **kwargs)

    return wrapper
