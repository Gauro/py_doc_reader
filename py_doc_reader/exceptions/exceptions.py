"""
Created on 27-Oct-2022
@author: Gaurav Ail
"""


class ConfigurationError(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message, errors)


class NonRecoverableException(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message, errors)


class RecoverableException(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message, errors)


class ValidationError(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message, errors)


class LoggingException(Exception):
    def __init__(self, message, errors=None):
        # Call the base class constructor with the parameters it needs
        super(Exception, self).__init__(message, errors)
