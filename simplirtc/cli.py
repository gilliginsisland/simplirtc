import sys
from typing import (
    Any,
    Callable,
    Coroutine,
    TypeVar,
    ParamSpec,
    cast,
)
import inspect
import asyncio
import argparse

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

SyncAsync = Callable[P, R] | Callable[P, Coroutine[Any, Any, R]]
Argument = tuple[tuple[Any, ...], dict[str, Any]]


class CLI:
    def __init__(self, *args: Argument, **kwargs: Any) -> None:
        """Initialize CLI with argparse and subparsers."""
        self._parser = argparse.ArgumentParser(**kwargs)
        self._subparsers = self._parser.add_subparsers(dest="command", required=True)

        for arg_args, arg_kwargs in args:
            self._parser.add_argument(*arg_args, **arg_kwargs)

    def command(self, *args: Argument) -> Callable[[SyncAsync], SyncAsync]:
        """Decorator to register a function as a CLI command with arguments."""
        def decorator(func: SyncAsync) -> SyncAsync:
            subparser = self._subparsers.add_parser(func.__name__, help=func.__doc__)

            for arg_args, arg_kwargs in args:
                subparser.add_argument(*arg_args, **arg_kwargs)

            # Set the function as the handler
            subparser.set_defaults(handler=func)
            return func
        return decorator

    def run(self) -> Any:
        """Parse CLI arguments and execute the corresponding command."""
        args = self._parser.parse_args()

        if not (handler := cast(SyncAsync | None, getattr(args, "handler", None))):
            self._parser.print_help()
            return 1

        kwargs = {
            key: getattr(args, key)
            for key in inspect.signature(handler).parameters.keys()
        }

        try:
            if asyncio.iscoroutine(ret := handler(**kwargs)):
                return asyncio.run(ret)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        return ret

def argument(*args: Any, **kwargs: Any) -> Argument:
    """Helper function to structure arguments for @cli.command and global flags."""
    return args, kwargs
