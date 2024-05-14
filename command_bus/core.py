import logging
from copy import deepcopy
from typing import Type, Dict, List
from contextlib import contextmanager

from exceptions import MissingHandler, OverWritingHandler
from interfaces import ICommandBus, ICommand, ICommandHandler, IEventHandler, IEvent, IQueryHandler, IQuery, IResponse

logger = logging.getLogger(__name__)


class CommandBus(ICommandBus):
    """
    A CommandBus handles command messages, which signal the user's intention.
    One command is handled by exactly one handler. A command does not return any values.
    One query is handled by exactly one handler. A query return any values, should be not change the state of the application.
    One event can be handled by any number of handlers ([0, inf]). Only holds primitives (strings, integers, booleans), not whole classes. Events should not return values.

    Methods:
        __init__: Initializes the CommandBus instance.
        register_command_handler: Registers a command handler for a specific command name.
        register_event_handler: Registers an event handler for a specific event name.
        register_query_handler: Registers a query handler for a specific query name.
        execute_command: Executes a command by dispatching it to the appropriate handler.
        execute_query: Executes a query by dispatching it to the appropriate handler.
        publish_event: Publishes an event to be handled by registered event handlers.
    """
    def __init__(self) -> None:
        self._command_handlers: Dict[str, ICommandHandler] = dict()
        self._event_handlers: Dict[str, List[IEventHandler]] = dict()
        self._query_handlers: Dict[str, IQueryHandler] = dict()
        self._published_events: List[IEvent] = list()

    @contextmanager
    def session(self):
        published_events_bkp = deepcopy(self._published_events)
        self._published_events = list()
        try:
            yield self
        finally:
            self._published_events = published_events_bkp

    def get_published_events(self) -> List[IEvent]:
        return self._published_events

    def flush_published_events(self) -> None:
        self._published_events = list()

    def subscribe_command(
            self,
            command_cls: Type[ICommand],
            command_handler: ICommandHandler
    ) -> None:
        command_name: str = command_cls.__name__
        if command_name in self._command_handlers:
            raise OverWritingHandler(
                "A handler for the command {} already exists.".format(command_name))
        self._command_handlers[command_name] = command_handler

    def publish_command(
            self,
            command: ICommand
    ) -> None:
        command_name: str = command.__class__.__name__
        if command_name not in self._command_handlers:
            raise MissingHandler(
                "Publishing command {} failed because of missing subscriber.".format(command))
        command_handler: ICommandHandler = self._command_handlers[command_name]
        command_handler(command)

    def subscribe_event(
            self,
            event_cls: Type[IEvent],
            event_handlers: List[IEventHandler]
    ) -> None:
        event_name: str = event_cls.__name__
        if event_name not in self._event_handlers.keys():
            self._event_handlers[event_name] = []
        for event_handler in event_handlers:
            if event_handler not in self._event_handlers[event_name]:
                self._event_handlers[event_name].append(event_handler)

    def publish_event(
            self,
            event: IEvent
    ) -> None:
        event_name: str = event.__class__.__name__
        if event_name not in self._event_handlers:
            logger.warning(
                "Publishing event {} failed because of missing subscriber.".format(event_name))
            return
        self._published_events.append(event)
        event_handlers: List[IEventHandler] = self._event_handlers.get(event_name, [])
        for event_handler in event_handlers:
            event_handler(event)

    def subscribe_query(
            self,
            query_cls: Type[IQuery],
            query_handler: IQueryHandler
    ) -> None:
        query_name: str = query_cls.__name__
        if query_name in self._query_handlers:
            raise OverWritingHandler(
                "A handler for the query {} already exists.".format(query_name))
        self._query_handlers[query_name] = query_handler

    def publish_query(
            self,
            query: IQuery
    ) -> IResponse:
        query_name: str = query.__class__.__name__
        if query_name not in self._query_handlers:
            raise MissingHandler(
                "Publishing query {} failed because of missing subscriber.".format(query))
        query_handler: IQueryHandler = self._query_handlers[query_name]
        response: IResponse = query_handler(query)
        return response
