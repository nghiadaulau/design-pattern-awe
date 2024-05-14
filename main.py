from dataclasses import dataclass

from command_bus.core import CommandBus
from command_bus.interfaces import ICommand, IEvent


class Command(ICommand):
    pass


class Event(IEvent):
    pass


@dataclass
class RegisterUserCommand(Command):
    user_name: str


@dataclass
class UserRegisteredEvent(Event):
    user_name: str


@dataclass
class NewUserGreetedEvent(Event):
    user_name: str


class RegisterUser:

    def __init__(self, messenger) -> None:
        self._messenger = messenger

    def __call__(self, command: RegisterUserCommand) -> None:
        self._messenger.publish_event(
            UserRegisteredEvent(command.user_name))


class GreetNewUser:

    def __init__(self, messenger) -> None:
        self._messenger = messenger

    def __call__(self, event: UserRegisteredEvent) -> None:
        self._messenger.publish_event(
            NewUserGreetedEvent(event.user_name))


command_bus = CommandBus()
register_user = RegisterUser(command_bus)
greet_new_user = GreetNewUser(command_bus)
command_bus.subscribe_command(RegisterUserCommand, register_user)
command_bus.subscribe_event(UserRegisteredEvent, [greet_new_user])
command_bus.publish_command(RegisterUserCommand("KaiKie"))
