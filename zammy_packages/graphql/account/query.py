import graphene
from zammy_packages.graphql.core.decorators import id_token_authenticaion


class UserType(graphene.ObjectType):
    uuid = graphene.String()
    username = graphene.String()
    email = graphene.String()
    login_type = graphene.String()


class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType)

    @id_token_authenticaion
    def resolve_me(user, *info, **kwargs):
        return {
            "uuid": user.uuid,
            "username": user.username,
            "email": user.email,
            "login_type": user.login_type,
        }
