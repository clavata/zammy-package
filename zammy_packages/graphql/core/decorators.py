from zammy_packages.graphql.core.authentication import CognitoAuthentication
from zammy_packages.graphql.core.mutations import AuthenticatedMutation
from zammy_packages.account.models import ZammyAccount


def id_token_authenticaion(func):
    def wrapper(*info, **kwargs):
        claims = AuthenticatedMutation.authenticate(info[1])
        try:
            user = ZammyAccount.objects.get(email=claims["email"])
        except ZammyAccount.DoesNotExist:
            raise Exception("해당 유저는 존재하지 않습니다.")
        return func(user, *info, **kwargs)

    return wrapper
