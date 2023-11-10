
class Response:
    """Object Response.

    Args:
        status_code(int): Status code http.
        message(str): A message.
        token(str): Token generated.
        error(str): Error message.
    """
    def __init__(
        self,
        status_code: int = None,
        message: str = None,
        token: str = None,
        error: str = None
            ):

        self.status_code = status_code
        self.message = message
        self.token = token
        self.error = error


class Payload:
    """Payload Jwt Response.

    Args:
        exp(int): Timeline to expire.
        iat(str): Timeline of creation.
        sub(str): Token identifier.
        uuid(str): Uuid token identifier.
        error(str): Error message.
    """
    def __init__(
        self,
        exp: int = None,
        iat: str = None,
        sub: str = None,
        uuid: str = None,
        error: str = None
            ):

        self.exp = exp
        self.iat = iat
        self.sub = sub
        self.uuid = uuid
        self.error = error
