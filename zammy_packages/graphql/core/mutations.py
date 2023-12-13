import graphene
from zammy_packages.graphql.core.authentication import CognitoAuthentication


class AuthenticationMutation(graphene.Mutation, CognitoAuthentication):
    class Meta:
        abstract = True

    @classmethod
    def mutate(cls, *info, **kwargs):
        pass

    @classmethod
    def perform_mutation(cls, result, *info, **kwargs):
        pass
