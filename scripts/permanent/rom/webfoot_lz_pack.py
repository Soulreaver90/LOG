# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Source: buusfury-decomp commit 8870c2f, tools/webfoot/webfoot_lz.py
# (repository LICENSE: MPL-2.0; the source file itself carries no header).
# Copied verbatim: constants, ContainerError, _WordBitWriter, length_bias,
# _gamma_cost and pack() (source lines 8-9, 22-23, 313-479). Nothing else.
# Copied for the 2026-10-22 tool review round trip; not edited.

r"""
webfoot_lz_pack.py - Pack bytes into a LoG II (Webfoot) codec stream: the compressor half of webfoot_decompress.

Usage:   from rom.webfoot_lz_pack import pack    pack(payload, kind=1) -> {u32 kind, u32 len} + stream
Source:  a copy of scripts\one-time\2026-10-22-modder-tool-review\vendor\webfoot_lz_pack.py (Buu's Fury decomp
         commit 8870c2f, tools/webfoot/webfoot_lz.py, MPL-2.0, notice above). Round trip proven on 1,656 r27 frames
         and 6 synthetic payloads (bible TRV row). First used by patches.beam_struggle (2026-10-25).
Rules:   The code below this block is the vendor copy, not edited. The stream sets 8-bit literal mode before its
         first literal, so the decoder's entry r3 does not matter. Callers decode each stream with
         webfoot_decompress.decompress before they write it.
"""
from __future__ import annotations

import struct


STORED = 0
PACKED_KINDS = (1, 2)


class ContainerError(ValueError):
    pass


_ENCODER_DISTANCE_BITS = 8
_ENCODER_DISTANCE_MASK = (1 << _ENCODER_DISTANCE_BITS) - 1

_MAX_MATCH = 255
_MAX_WINDOW = 0xFFFF

_CHAIN_LIMIT = 32


class _WordBitWriter:

    __slots__ = ("_words", "_current", "_count")

    def __init__(self) -> None:
        self._words: list[int] = []
        self._current = 0
        self._count = 0

    def bit(self, value: int) -> None:
        self._current = ((self._current << 1) | (value & 1)) & 0xFFFFFFFF
        self._count += 1
        if self._count == 32:
            self._words.append(self._current)
            self._current = 0
            self._count = 0

    def put(self, value: int, width: int) -> None:
        for shift in range(width - 1, -1, -1):
            self.bit((value >> shift) & 1)

    def gamma(self, value: int) -> None:
        if value < 2:
            raise ContainerError(f"gamma cannot encode {value}")
        for shift in range(value.bit_length() - 2, -1, -1):
            self.bit((value >> shift) & 1)
            self.bit(0 if shift == 0 else 1)

    def write_end_marker(self) -> None:
        self.put(0, 12)

    def finish(self) -> bytes:
        while self._count:
            self.bit(0)
        return b"".join(struct.pack("<I", word) for word in self._words)


def length_bias(distance: int) -> int:
    if distance >= 0x10000:
        return 3
    if distance >= 0x37FF:
        return 2
    if distance >= 0x027F:
        return 1
    if distance <= 0x007F:
        return 4
    return 0


def _gamma_cost(value: int) -> int:
    return 2 * (value.bit_length() - 1)


def pack(payload: bytes, *, kind: int = PACKED_KINDS[1]) -> bytes:
    if kind not in PACKED_KINDS:
        raise ContainerError(
            f"pack emits a packed container; kind {kind!r} is not one of "
            f"{PACKED_KINDS}"
        )
    writer = _WordBitWriter()
    writer.bit(0)
    writer.bit(0)
    writer.bit(1)
    writer.put(0, 4)
    writer.bit(0)
    writer.bit(1)

    positions: dict[bytes, list[int]] = {}
    total = len(payload)
    cursor = 0
    previous_distance = 1

    while cursor < total:
        best_cost = 1 + 8
        best_length = 1
        best_token: tuple[str, int, int] = ("literal", 0, 1)

        for short in range(1, min(15, cursor + 1)):
            if payload[cursor - short] == payload[cursor]:
                if 8 < best_cost:
                    best_cost, best_length = 8, 1
                    best_token = ("one", short, 1)
                break

        if cursor + 3 <= total:
            key = payload[cursor : cursor + 3]
            for start in reversed(positions.get(key, ())[-_CHAIN_LIMIT:]):
                distance = cursor - start
                if distance <= 0 or distance > _MAX_WINDOW:
                    continue
                length = 3
                limit = min(_MAX_MATCH, total - cursor)
                while (
                    length < limit
                    and payload[start + length] == payload[cursor + length]
                ):
                    length += 1

                if 1 <= distance <= 127 and 2 <= length <= 5:
                    cost = 3 + 7 + 2
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("short", distance, length)

                if distance == previous_distance:
                    cost = 2 + _gamma_cost(2) + _gamma_cost(length)
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("previous", distance, length)

                count = length - length_bias(distance)
                if count >= 2:
                    code = (distance >> _ENCODER_DISTANCE_BITS) + 3
                    cost = (
                        2
                        + _gamma_cost(code)
                        + _ENCODER_DISTANCE_BITS
                        + _gamma_cost(count)
                    )
                    if cost / length < best_cost / best_length:
                        best_cost, best_length = cost, length
                        best_token = ("long", distance, count)

        token_kind, distance, argument = best_token
        if token_kind == "literal":
            writer.bit(1)
            writer.put(payload[cursor], 8)
        elif token_kind == "one":
            writer.bit(0)
            writer.bit(0)
            writer.bit(1)
            writer.put(distance + 1, 4)
        elif token_kind == "short":
            writer.bit(0)
            writer.bit(0)
            writer.bit(0)
            writer.put(distance, 7)
            writer.put(argument - 2, 2)
            previous_distance = distance
        elif token_kind == "previous":
            writer.bit(0)
            writer.bit(1)
            writer.gamma(2)
            writer.gamma(argument)
        else:
            writer.bit(0)
            writer.bit(1)
            writer.gamma((distance >> _ENCODER_DISTANCE_BITS) + 3)
            writer.put(distance & _ENCODER_DISTANCE_MASK, _ENCODER_DISTANCE_BITS)
            writer.gamma(argument)
            previous_distance = distance

        for index in range(cursor, min(cursor + best_length, total - 2)):
            positions.setdefault(payload[index : index + 3], []).append(index)
        cursor += best_length

    writer.write_end_marker()
    return struct.pack("<II", kind, total) + writer.finish()
