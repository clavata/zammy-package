import graphene
import jwt
import requests
import time
import urllib.request
import json
from django.conf import settings
from zammy_packages.graphql.core.authentication import CognitoAuthentication
from zammy_packages.account.models import ZammyAccount


GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
LINE_CLIENT_ID = settings.LINE_CLIENT_ID
LINE_CLIENT_SECRET = settings.LINE_CLIENT_SECRET
LINE_REDIRECT_URI = settings.LINE_REDIRECT_URI
COGNITO_AWS_REGION = settings.COGNITO_AWS_REGION
COGNITO_USER_POOL = settings.COGNITO_USER_POOL
COGNITO_AUDIENCE = settings.COGNITO_AUDIENCE


class AuthenticationMutation(graphene.Mutation, CognitoAuthentication):
    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, *info, **kwargs):
        pass

    @classmethod
    def perform_mutation(cls, result, *info, **kwargs):
        pass


class OAuthIDTokenVerifier:
    content_type = "application/x-www-form-urlencoded"

    def __init__(self, id_token):
        self.id_token = id_token

    def verify_cognito_id_token(self):
        keys_url = (
            "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
                COGNITO_AWS_REGION, COGNITO_USER_POOL
            )
        )
        with urllib.request.urlopen(keys_url) as f:
            response = f.read()

        keys = json.loads(response.decode("utf-8"))["keys"]
        if self.id_token is None:
            raise Exception("Token does not exist")
        try:
            headers = jwt.get_unverified_header(self.id_token)
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
        response = jwt.decode(
            self.id_token, algorithms=["RS256"], options={"verify_signature": False}
        )
        if time.time() > response["exp"]:
            raise Exception("Token is expired")
        return response

    def verify_google_id_token(self):
        url = "https://oauth2.googleapis.com/tokeninfo"
        payload = {
            "id_token": self.id_token,
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(response.json())
        return response.json()

    def verify_line_id_token(self):
        url = "https://api.line.me/oauth2/v2.1/verify"
        payload = {
            "id_token": self.id_token,
            "client_id": LINE_CLIENT_ID,
        }
        response = requests.post(
            url, headers={"Content-type": self.content_type}, data=payload
        )
        if response.status_code != 200:
            raise Exception(response.json())
        return response.json()


class AuthenticatedMutation(graphene.Mutation):
    class Meta:
        abstract = True

    @staticmethod
    def authenticate(info):
        token = info.context.META.get("HTTP_AUTHORIZATION")
        if token is None:
            raise Exception("Token does not exist")
        claims = jwt.decode(
            token, algorithms=["RS256"], options={"verify_signature": False}
        )
        if "cognito" in claims["iss"]:
            OAuthIDTokenVerifier(token).verify_cognito_id_token()
        elif "google" in claims["iss"]:
            OAuthIDTokenVerifier(token).verify_google_id_token()
            return {
                "login_type": "google",
                "email": claims["email"],
                "username": claims["name"],
            }
        elif "line" in claims["iss"]:
            OAuthIDTokenVerifier(token).verify_line_id_token()

    @classmethod
    def mutate(cls, result, *info, **kwargs):
        user_info = cls.authenticate(info[0])
        try:
            user = ZammyAccount.objects.get(
                email=user_info["email"], login_type=user_info["login_type"]
            )
        except ZammyAccount.DoesNotExist:
            raise Exception("User does not exist")
        return cls.perform_mutation(cls, user, *info, **kwargs)

    @classmethod
    def perform_mutation(cls, user, *info, **kwargs):
        pass
