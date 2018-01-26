import exceptions
def check_type(name, var, var_type, exc=exceptions.MooseDocsException):
    if not isinstance(var, var_type):
        msg = "The argument '{}' must be of type {} but {} was provided."
        raise exc(msg.format(name, type(var), var_type))
