import jwt
import uuid
from datetime import datetime, timedelta
from .utils import Response, Payload


class AuthToken:
    """AuthToken Class, generate token jwt.

    Args:
        sub(str): Identifier token.
        exp(int): Amount of time expire (minutes).
        secret_key(str): Token key.
        algorithm(str): Default HS256.
    """

    def __init__(
        self,
        sub: str,
        exp: int,
        secret_key: str,
        algorithm: str = 'HS256'
            ):
        self._sub = sub
        self._exp = exp
        self._secret_key = secret_key
        self._algorithm = algorithm

    def encode(self) -> str:
        """Get token encode.

        Returns:
            Response(auth_token.utils.Response): Reponse object.
        """
        payload = {
            'exp': self.__get_expire_in(),
            'iat': datetime.utcnow(),
            'sub': self._sub,
            'uuid': self.__get_uuid()
        }
        data = jwt.encode(
            payload,
            self._secret_key,
            algorithm=self._algorithm
        )

        return Response(
            status_code=200,
            message='ok',
            token=data.decode()
        )

    def __get_expire_in(self) -> timedelta:
        """Get time of expiration in minutes.

        Returns:
            timedelta(datetime.timedelta): Time of expiration in minutes.
        """
        now = datetime.utcnow()
        return now + timedelta(minutes=self._exp)

    def __get_uuid(self) -> str:
        """Generate uuid.

        Returns:
            uuid(uuid.uuid4): Uuid identifier.
        """
        return str(uuid.uuid4())

    def decode(self, token) -> Payload:
        """Decode token.

        Args:
            token(str): Token jwt.

        Returns:
            Payload(auth_token.utils.Payload): Payload Object.
        """
        try:
            data = jwt.decode(
                token,
                self._secret_key,
                algorithms=self._algorithm
            )

            return Payload(
                exp=data.get('exp'),
                iat=data.get('iat'),
                sub=data.get('sub'),
                uuid=data.get('uuid')
            )
        except jwt.ExpiredSignatureError:
            return Payload(
                error='expired_token'
            )
        except Exception:
            return Payload(
                error='invalid_token'
            )
