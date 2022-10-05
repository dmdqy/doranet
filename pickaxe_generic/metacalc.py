"""
Contains metadata calculator classes.
"""

import collections.abc
import dataclasses
import typing

from . import interfaces, metadata


@typing.final
@dataclasses.dataclass(frozen=True)
class GenerationCalculator(metadata.MolPropertyFromRxnCalc[int]):
    __slots__ = "gen_key"

    gen_key: collections.abc.Hashable

    @property
    def key(self) -> collections.abc.Hashable:
        return self.gen_key

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(
            molecule_keys=frozenset((self.gen_key,))
        )

    @property
    def resolver(self) -> metadata.MetaDataResolverFunc[int]:
        return min

    def __call__(
        self,
        data: interfaces.DataPacketE[interfaces.MolDatBase],
        rxn: interfaces.ReactionExplicit,
        prev_value: typing.Optional[int] = None,
    ) -> typing.Optional[int]:
        if data in rxn.reactants:
            return None
        cur_gen = None
        for reactant in rxn.reactants:
            if reactant.meta is None or self.gen_key not in reactant.meta:
                return None
            if cur_gen is None:
                cur_gen = reactant.meta[self.gen_key] + 1
            cur_gen = max(cur_gen, reactant.meta[self.gen_key] + 1)
        if cur_gen is None:
            return None
        if prev_value is not None and prev_value < cur_gen:
            return None
        if (
            data.meta is not None
            and self.gen_key in data.meta
            and data.meta[self.gen_key] <= cur_gen
        ):
            return None
        return cur_gen
