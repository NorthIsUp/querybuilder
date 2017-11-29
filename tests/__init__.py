# -*- coding: utf-8 -*-

"""Unit test package for querybuilder."""


from __future__ import absolute_import

# Standard Library
from functools import wraps

# External Libraries
import pytest


def fixture(*args, **kwargs):
    """
    Same args and kwargs as pytest.fixture with the following additions.

    Args:
        autoparam (bool): Instead of operating as a decorator just automatically create a fixture that returns `request.param`
        **kwargs: kwargs is automatically converted to id, param pairs for the purpose of parametrized tests.

    Returns: a pytest.fixture function or method.

    """
    def decorator_factory(func):
        fixture_kwargs = {}
        if 'scope' in kwargs:
            fixture_kwargs['scope'] = kwargs.pop('scope')

        if 'autouse' in kwargs:
            fixture_kwargs['autouse'] = kwargs.pop('autouse')

        if 'params' in kwargs:
            fixture_kwargs['params'] = list(kwargs.pop('params'))

        if 'ids' in kwargs:
            fixture_kwargs['ids'] = list(kwargs.pop('ids'))

        if kwargs:
            fixture_kwargs.setdefault('params', []).extend(kwargs.values())
            fixture_kwargs.setdefault('ids', []).extend(kwargs.keys())

        if args:
            fixture_kwargs.setdefault('params', []).extend(args)

        return pytest.fixture(**fixture_kwargs)(func)

    if kwargs.pop('autoparam', False):
        @make_class_agnostic
        def autoparam(request):
            return request.param

        return decorator_factory(autoparam)

    return decorator_factory


def patcher(
    path_or_obj,
    key=None,
    raising=False,
    autouse=True,
    automock=False,
    automagicmock=False,
    configure_mock=None,
    **mock_args
):
    """A helper function for using monkeypatch with py.test

    patcher can be used as a decorator or a function.


    Args:
        path_or_obj: A string of a python path to patch or an object to patch
        key: If an object is provided, this is the name of the attribute to patch
        raising: Raise an exception if the attribute to patch does not already exits
        autouse: If True the patch will happen automatically for every test in the scope,
            otherwise it must be passed in as a pytest fixture.
        automock: Automatically return a Mock object
        automagicmock: Automatically return a MagicMock object
        dict configure_mock: If automock or automagicmock is enabled then pass this dict to mock.configure_mock
        return_value: If automock and automagicmock are False, then simply return this value.
            If they are true then return_value is passed normally to the mock class.
        **mock_args: Args to be passed into mock_class(**mock_args)

    Returns pytest.fixture: a vailid pytest fixture function

    Examples:

        As a simple decorator with a path to patch. Similar to mock.patch

        >>> @patcher('path.to.func')
        ... def patcher_func():
        ...     return 'hello'
        >>> # Equivalent to:
        >>> patcher_func = patcher('path.to.func', return_value='hello')
        >>> # Note that there is no way to use fixture arguments when using patcher in this example

        As a simple decorator with an object to patch. This will replace
          `class_to_patch.attribute` with the return value of patcher_func
        >>> class SomeClass():
        ...     def foo(self): pass

        >>> @patcher(SomeClass, 'foo')
        ... def patcher_func(any, fixture, you, want):
        ...     return lambda self: 'hi'

        This example will fail if `SomeClass.attribute` does not already exist
        >>> @patcher(SomeClass, 'attribute', raising=True)
        ... def patcher_func(any, fixture, you, want):
        ...     return lambda self: 'hi'
    """
    def decorator_factory(func):
        """
        py.test introsepects the names of arguments in functions to pass in fixtures
        This means we need to dynamically construct the inner call to `func` to contain
        these names.
        """
        from _pytest.compat import getfuncargnames

        args = getfuncargnames(func)

        monkey_args = set(args + ('monkeypatch', ))

        wrapper_str = """
@pytest.fixture(autouse={autouse})
def {fixture_name}({monkey_args}):
    val = func({args})
    if isinstance(path_or_obj, str):
        monkeypatch.setattr(path_or_obj, val, raising=raising)
    elif isinstance(path_or_obj, (tuple, list)):
        for item in path_or_obj:
            monkeypatch.setattr(item, val, raising=raising)
    else:
        monkeypatch.setattr(path_or_obj, key, value=val, raising=raising)
    return val
        """.format(
            fixture_name=func.__name__,
            args=', '.join(args),
            monkey_args=', '.join(monkey_args),
            autouse=repr(autouse)
        )

        # Execute the template string in a temporary namespace and support
        # tracing utilities by setting a value for frame.f_globals['__name__']
        namespace = {
            'func': func,
            'key': key,
            'path_or_obj': path_or_obj,
            'pytest': pytest,
            'raising': raising,
            'wraps': wraps,
            '__name__': 'patcher_%s' % func.__name__,
        }
        exec(wrapper_str, namespace)
        return namespace[func.__name__]

    if automock or automagicmock or configure_mock:
        @make_class_agnostic
        def _func(*args):
            # creation of the mock object must be scoped in this _func
            mock_class = None
            if automock:
                mock_class = mock.Mock
            elif automagicmock:
                mock_class = mock.MagicMock

            mock_instance = mock_class(**mock_args)
            if configure_mock:
                mock_instance.configure_mock(**configure_mock)

            return mock_instance
        return decorator_factory(_func)

    elif 'return_value' in mock_args:
        return_value = mock_args.pop('return_value')

        @make_class_agnostic
        def _func(*args):
            return return_value

        return decorator_factory(_func)

    return decorator_factory


def parametrize(**kwargs):

    def decorator_factory(func):
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                func = pytest.mark.parametrize(key, value)(func)
            else:
                func = pytest.mark.parametrize(key, [value])(func)
        return func
    return decorator_factory


def is_inside_class():
    """
    Returns: Class name of encapsulating class or None
    """
    import inspect
    frames = inspect.stack()

    for frame in frames[1:]:
        if frame[3] == "<module>":
            # At module level, go no further
            return
        elif '__module__' in frame[0].f_code.co_names:
            # found the encapsulating class, go no further
            return frame[0].f_code.co_name


def make_class_agnostic(func):
    """
    make fixtures that don't care if it is in a class or not work fine

    >>> @make_class_agnostic
    ... def inner_func(request):
    ...     return request
    ...
    >>> class Foo():
    ...     bar = inner_func
    ...
    >>> Foo.bar('hi') == 'hi'
    True
    >>> inner_func('hi') == 'hi'
    True
    """

    if is_inside_class():
        def wrapper(self, request):
            return func(request)

    else:
        def wrapper(request):
            return func(request)

    return wrapper
