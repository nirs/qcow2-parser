#!/usr/bin/python
# qcow2-parser
# Copyright (C) 2017 Nir Soffer <nirsof@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

"""
qcow2 header parser
"""

import struct

BIG_ENDIAN = ">"


class Struct(object):

    def __init__(self, fields, byte_order=BIG_ENDIAN):
        self.keys = [key for key, _ in fields]
        fmt = byte_order + "".join(code for _, code in fields)
        self.struct = struct.Struct(fmt)

    def unpack_from(self, f):
        data = f.read(self.struct.size)
        values = self.struct.unpack(data)
        return {key: value for key, value in zip(self.keys, values)}


HEADER_V2 = Struct([
    ("magic", "I"),
    ("version", "I"),
    ("backing_file_offset", "Q"),
    ("backing_file_size", "I"),
    ("cluster_bits", "I"),
    ("size", "Q"),
    ("crypt_method", "I"),
    ("l1_size", "I"),
    ("l1_table_offset", "Q"),
    ("refcount_table_offset", "Q"),
    ("refcount_table_clusters", "I"),
    ("nb_snapshots", "I"),
    ("snapshots_offset", "Q"),
])

HEADER_V3 = Struct([
    ("incompatible_features", "Q"),
    ("compatible_features", "Q"),
    ("refcount_order", "I"),
    ("header_length", "I"),
])


def parse(file):
    info = HEADER_V2.unpack_from(file)
    if info["version"] == 3:
        v3_info = HEADER_V3.unpack_from(file)
        info.update(v3_info)
    return info


if __name__ == "__main__":
    import sys
    import json
    filename = sys.argv[1]
    with open(filename) as f:
        info = parse(f)
        print json.dumps(info, indent=4, sort_keys=True)
