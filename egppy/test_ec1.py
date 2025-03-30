"""EGP Execution Context generated on 2025-03-30T16:07:26.856975"""

#  _____ ____ ____    _____                  ____            _            _
# | ____/ ___|  _ \  | ____|_  _____  ___   / ___|___  _ __ | |_ _____  _| |_
# |  _|| |  _| |_) | |  _| \ \/ / _ \/ __| | |   / _ \| '_ \| __/ _ \ \/ / __|
# | |__| |_| |  __/  | |___ >  <  __/ (__  | |__| (_) | | | | ||  __/>  <| |_
# |_____\____|_|     |_____/_/\_\___|\___|  \____\___/|_| |_|\__\___/_/\_\__|
#
#
#  \(O)/   Erasmus Genetic Programming (EGP) v0.1
#   |@|    Released 11-Feb-2023 11:07:00 UTC under MIT license
#  ~~~~~   Copyright (c) 2023 Shapedsundew9.  https://github.com/Shapedsundew9
#
from random import getrandbits


def f_0(i: tuple[int]) -> int:
    """Signature: 94ed53e02f4b722a14cfb7e82264a198f131fafeb6c6c777291eac2afbad73d9
    Created: 2025-03-29 22:05:08.489847+00:00
    License: MIT
    Creator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f
    Generation: 2
    """
    t0 = 1
    o0 = i[0] >> t0
    return o0


def f_1() -> int:
    """Signature: d164b93d0bbe4297476fea3c9cd6bc2da48c6ecc7c43e8a7035a15fab2f31c0a
    Created: 2025-03-29 22:05:08.489847+00:00
    License: MIT
    Creator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f
    Generation: 2
    """
    t0 = 64
    o0 = getrandbits(t0)
    return o0


def f_2(i: tuple[int]) -> tuple[int, int]:
    """Signature: c3efa5f34e03343cd6efd96fed68e6309e48fd9b7d388f12851b04c25483e885
    Created: 2025-03-29 22:05:08.489847+00:00
    License: MIT
    Creator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f
    Generation: 4
    """
    t1 = f_1()
    t0 = f_0((t1,))
    o0 = i[0] ^ t0
    return o0, o1
