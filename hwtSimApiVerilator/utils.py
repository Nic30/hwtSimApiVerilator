from typing import List, Optional

from hwt.hdl.types.array import HArray
from hwt.hdl.types.bits import Bits
from hwt.synthesizer.unit import Unit
from ipCorePackager.constants import DIRECTION


def collect_signals(top: Unit):
    """
    collect list of all signals in the component
    format (
    name: Tuple[str], phy_name:str, is_read_only: int,
    is_signed: int, size: Tuple[int])
    """
    accessible_signals = []
    _collect_signals(top, accessible_signals, None, [], True)
    return accessible_signals


def _collect_signals(top: Unit,
                     accessible_signals: List,
                     top_name: Optional[str],
                     name_prefix: List[str],
                     is_top: bool):
    VERILATOR_NAME_SEPARATOR = "__DOT__"
    # {sig: is output}
    io_signals = {}
    if is_top:
        for p in top._entity.ports:
            is_read_only = p.direction == DIRECTION.OUT
            if p.direction == DIRECTION.IN:
                s = p.dst
            else:
                s = p.src
            io_signals[s] = is_read_only

    if top_name is None:
        top_name = top._name

    for s in top._ctx.signals:
        if s.hidden:
            continue
        is_read_only = io_signals.get(s, True)
        t = s._dtype
        size = []
        while isinstance(t, HArray):
            size.append(int(t.size))
            t = t.element_t

        if isinstance(t, Bits):
            size.append(t.bit_length())
            is_signed = int(bool(t.signed))
        else:
            continue

        name = (*name_prefix, s.name)
        if s in io_signals:
            phy_name = VERILATOR_NAME_SEPARATOR.join(name)
        else:
            phy_name = VERILATOR_NAME_SEPARATOR.join([top_name, *name])

        accessible_signals.append(
            (name, phy_name, is_read_only, is_signed, size)
        )

    is_top = False
    for u in top._units:
        _name_prefix = (*name_prefix, u._entity._name)
        _collect_signals(u, accessible_signals, top_name, _name_prefix, is_top)

