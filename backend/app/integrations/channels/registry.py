"""Channel adapter registry.

A lightweight registry mapping `ChannelType` to adapter classes. It is empty
until concrete adapters are implemented; the structure exists so that adding a
channel later is a self-contained change (implement adapter -> register it)
with no edits to the conversation/AI layers.
"""

from app.integrations.channels.base import BaseChannelAdapter, ChannelType

_REGISTRY: dict[ChannelType, type[BaseChannelAdapter]] = {}


def register_channel(
    adapter_cls: type[BaseChannelAdapter],
) -> type[BaseChannelAdapter]:
    """Register an adapter class (usable as a decorator)."""
    _REGISTRY[adapter_cls.channel_type] = adapter_cls
    return adapter_cls


def get_adapter_class(channel: ChannelType) -> type[BaseChannelAdapter]:
    """Return the adapter class for a channel, or raise if unregistered."""
    try:
        return _REGISTRY[channel]
    except KeyError as exc:
        raise LookupError(f"No adapter registered for channel: {channel}") from exc


def available_channels() -> list[ChannelType]:
    """Channels that currently have a registered adapter."""
    return list(_REGISTRY.keys())
