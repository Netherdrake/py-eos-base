class EosdNoResponse(BaseException):
    pass


class RPCError(BaseException):
    pass


class WeakPasswordError(ValueError):
    pass
