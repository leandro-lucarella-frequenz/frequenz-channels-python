# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Predicates to be used in conjuntion with `Receiver.filter()`."""


from typing import Callable, Final, Generic, TypeGuard

from frequenz.channels._generic import ChannelMessageT


class _Sentinel:
    """A sentinel to denote that no value has been received yet."""

    def __str__(self) -> str:
        """Return a string representation of this sentinel."""
        return "<no value received yet>"


_SENTINEL: Final[_Sentinel] = _Sentinel()


class OnlyIfPrevious(Generic[ChannelMessageT]):
    """A predicate to check if a message has a particular relationship with the previous one.

    This predicate can be used to filter out messages based on a custom condition on the
    previous and current messages. This can be useful in cases where you want to
    process messages only if they satisfy a particular condition with respect to the
    previous message.

    Tip:
        If you want to use `==` as predicate, you can use the
        [`ChangedOnly`][frequenz.channels.experimental.ChangedOnly] predicate.

    Example: Receiving only messages that are not the same instance as the previous one.
        ```python
        from frequenz.channels import Broadcast
        from frequenz.channels.experimental import OnlyIfPrevious

        channel = Broadcast[int | bool](name="example")
        receiver = channel.new_receiver().filter(OnlyIfPrevious(lambda old, new: old is not new))
        sender = channel.new_sender()

        # This message will be received as it is the first message.
        await sender.send(1)
        assert await receiver.receive() == 1

        # This message will be skipped as it is the same instance as the previous one.
        await sender.send(1)

        # This message will be received as it is a different instance from the previous
        # one.
        await sender.send(True)
        assert await receiver.receive() is True
        ```

    Example: Receiving only messages if they are bigger than the previous one.
        ```python
        from frequenz.channels import Broadcast
        from frequenz.channels.experimental import OnlyIfPrevious

        channel = Broadcast[int](name="example")
        receiver = channel.new_receiver().filter(
            OnlyIfPrevious(lambda old, new: new > old, first_is_true=False)
        )
        sender = channel.new_sender()

        # This message will skipped as first_is_true is False.
        await sender.send(1)

        # This message will be received as it is bigger than the previous one (1).
        await sender.send(2)
        assert await receiver.receive() == 2

        # This message will be skipped as it is smaller than the previous one (1).
        await sender.send(0)

        # This message will be skipped as it is not bigger than the previous one (0).
        await sender.send(0)

        # This message will be received as it is bigger than the previous one (0).
        await sender.send(1)
        assert await receiver.receive() == 1

        # This message will be received as it is bigger than the previous one (1).
        await sender.send(2)
        assert await receiver.receive() == 2
    """

    def __init__(
        self,
        predicate: Callable[[ChannelMessageT, ChannelMessageT], bool],
        *,
        first_is_true: bool = True,
    ) -> None:
        """Initialize this instance.

        Args:
            predicate: A callable that takes two arguments, the previous message and the
                current message, and returns a boolean indicating whether the current
                message should be received.
            first_is_true: Whether the first message should be considered as satisfying
                the predicate. Defaults to `True`.
        """
        self._predicate = predicate
        self._last_message: ChannelMessageT | _Sentinel = _SENTINEL
        self._first_is_true = first_is_true

    def __call__(self, message: ChannelMessageT) -> bool:
        """Return whether `message` is the first one received or different from the previous one."""

        def is_message(
            value: ChannelMessageT | _Sentinel,
        ) -> TypeGuard[ChannelMessageT]:
            return value is not _SENTINEL

        old_message = self._last_message
        self._last_message = message
        if is_message(old_message):
            return self._predicate(old_message, message)
        return self._first_is_true

    def __str__(self) -> str:
        """Return a string representation of this instance."""
        return f"{type(self).__name__}:{self._predicate.__name__}"

    def __repr__(self) -> str:
        """Return a string representation of this instance."""
        return f"<{type(self).__name__}: {self._predicate!r} first_is_true={self._first_is_true!r}>"


class ChangedOnly(OnlyIfPrevious[object]):
    """A predicate to check if a message is different from the previous one.

    This predicate can be used to filter out messages that are the same as the previous
    one. This can be useful in cases where you want to avoid processing duplicate
    messages.

    Warning:
        This predicate uses the `!=` operator to compare messages, which includes all
        the weirdnesses of Python's equality comparison (e.g., `1 == 1.0`, `True == 1`,
        `True == 1.0`, `False == 0` are all `True`).

        If you need to use a different comparison, you can create a custom predicate
        using [`OnlyIfPrevious`][frequenz.channels.experimental.OnlyIfPrevious].

    Example:
        ```python
        from frequenz.channels import Broadcast
        from frequenz.channels.experimental import ChangedOnly

        channel = Broadcast[int](name="skip_duplicates_test")
        receiver = channel.new_receiver().filter(ChangedOnly())
        sender = channel.new_sender()

        # This message will be received as it is the first message.
        await sender.send(1)
        assert await receiver.receive() == 1

        # This message will be skipped as it is the same as the previous one.
        await sender.send(1)

        # This message will be received as it is different from the previous one.
        await sender.send(2)
        assert await receiver.receive() == 2
        ```
    """

    def __init__(self, *, first_is_true: bool = True) -> None:
        """Initialize this instance.

        Args:
            first_is_true: Whether the first message should be considered as different
                from the previous one. Defaults to `True`.
        """
        super().__init__(lambda old, new: old != new, first_is_true=first_is_true)

    def __str__(self) -> str:
        """Return a string representation of this instance."""
        return f"{type(self).__name__}"

    def __repr__(self) -> str:
        """Return a string representation of this instance."""
        return f"{type(self).__name__}(first_is_true={self._first_is_true!r})"
