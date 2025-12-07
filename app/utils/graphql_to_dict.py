from strawberry import UNSET


def graphql_to_dict(data):
    return {k: v for k, v in data.__dict__.items() if v is not UNSET}
