import jwt
import time
import json
import urllib.request
from django.conf import settings

from zammy_packages.account.models import ZammyAccount


region = settings.COGNITO_AWS_REGION
userpool_id = settings.COGNITO_USER_POOL
app_client_id = settings.COGNITO_AUDIENCE


class CognitoAuthentication:
    keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
        region, userpool_id
    )

    @classmethod
    def verify_to_cognito_id_token(cls, info):
        token = info.context.META.get("HTTP_AUTHORIZATION")
        with urllib.request.urlopen(cls.keys_url) as f:
            response = f.read()

        keys = json.loads(response.decode("utf-8"))["keys"]
        if token is None:
            raise Exception("Token does not exist")
        try:
            headers = jwt.get_unverified_header(token)
        except:
            raise Exception("Not a valid token value")
        kid = headers["kid"]
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]["kid"]:
                key_index = i
                break
        if key_index == -1:
            raise Exception("Public key not found in jwks.json")
        claims = jwt.decode(
            token, algorithms=["RS256"], options={"verify_signature": False}
        )
        if time.time() > claims["exp"]:
            raise Exception("Token is expired")
        return claims

    @classmethod
    def get_user_info_for_cognito(cls, info):
        claims = cls.verify_to_cognito_id_token(info[1])
        try:
            user = ZammyAccount.objects.get(email=claims["email"])
            return user
        except ZammyAccount.DoesNotExist:
            raise Exception("User does not exist")


def log_authenticaion(func):
    def wrapper(*info, **kwargs):
        claims = CognitoAuthentication.verify_to_cognito_id_token(info[1])
        try:
            user = ZammyAccount.objects.get(email=claims["email"])
        except ZammyAccount.DoesNotExist:
            raise Exception("해당 유저는 존재하지 않습니다.")

        try:
            if info[0].user_uuid != user.uuid:
                raise Exception("Access Denied")
        except AttributeError:
            pass
        return func(user, *info, **kwargs)

    return wrapper
