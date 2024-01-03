import graphene

from zammy_packages.graphql.core.mutations import AuthenticatedMutation
from zammy_packages.account.models import ZammyAccount


class UserCreateMutation(AuthenticatedMutation):
    uuid = graphene.String()
    email = graphene.String()
    username = graphene.String()
    login_type = graphene.String()

    @classmethod
    def mutate(cls, *info, **kwargs):
        user_info = cls.authenticate(info[1])
        user, not_exist = ZammyAccount.objects.get_or_create(
            email=user_info["email"],
            login_type=user_info["login_type"],
            username=user_info["username"],
        )
        if not_exist:
            return {
                "uuid": user.uuid,
                "email": user.email,
                "username": user.username,
                "login_type": user.login_type,
            }
        else:
            raise Exception("해당 유저는 이미 존재합니다.")


class UserMutation(graphene.ObjectType):
    user_create = UserCreateMutation.Field()
