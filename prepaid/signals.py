from django.dispatch import Signal

is_credits_cached = Signal(providing_args=['user'])
is_credits_cached.__doc__ = """
Signal send to verify if the credits is cached.
"""

set_credits_cache = Signal(providing_args=['user'])
set_credits_cache.__doc__ = """
Signal send to store the current credits on cache.
"""
get_credits_cache = Signal(providing_args=['user'])
get_credits_cache.__doc__ = """
Signal send to get the current credits on cache.
"""