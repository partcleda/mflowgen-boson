#!/usr/bin/env python3
# Copyright 2025 partcl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Normalize a boson structural netlist for OpenROAD:
 - top-level bus bits written as escaped scalar ports (\\name[i] ) become real vector ports, so bterms are name[i]
   (what a DEF/LEF pin template expects);
 - internal nets with brackets in escaped names (\\dbg[0]_1 ) become bracket-free (dbg_0__1) so DEF/guide/SPEF names
   agree across tools; the same renames are applied to the route-guide file.
usage: busify.py in.v out.v [in.guide out.guide]"""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
m = re.search(r'^\s*module\s+(\w+)\s*\((.*?)\);', s, re.S | re.M)
ports = [p.strip() for p in m.group(2).split(',')]
bit = re.compile(r'^\\(\w+)\[(\d+)\]\s*$')
buses = {}
for p in ports:
    mm = bit.match(p)
    if mm: buses.setdefault(mm.group(1), set()).add(int(mm.group(2)))
seen, newports = set(), []
for p in ports:
    mm = bit.match(p)
    name = mm.group(1) if mm else p
    if name not in seen: seen.add(name); newports.append(name)
body = s[m.end():]
decl = re.compile(r'^\s*(input|output|inout)\s+\\(\w+)\[(\d+)\]\s*;\s*$', re.M)
dirs = {n: d for d, n, i in decl.findall(body)}
body = decl.sub('', body)
vec = ''.join(f'  {dirs[n]} [{max(b)}:{min(b)}] {n};\n' for n, b in buses.items())
# internal nets: every `wire \name ;` whose escaped name contains brackets and is not a port bus bit
renames = {}
for n in re.findall(r'^\s*wire\s+\\(\S+)\s*;', body, re.M):
    if '[' in n and not (bit.match('\\' + n) and bit.match('\\' + n).group(1) in buses):
        renames[n] = re.sub(r'[\[\]]', '_', n)
def sub_escaped(mm):
    n = mm.group(1)
    b = bit.match('\\' + n)
    if b and b.group(1) in buses: return f'{b.group(1)}[{b.group(2)}]'
    if n in renames: return renames[n]
    return mm.group(0)
body = re.sub(r'\\(\S+)\s', sub_escaped, body)
out = s[:m.start()] + f'module {m.group(1)} ({", ".join(newports)});\n' + vec + body
open(dst, 'w').write(out)
print(f'busify: {len(buses)} bus(es): ' + ', '.join(f'{n}[{max(b)}:{min(b)}]' for n, b in buses.items()) + f'; {len(renames)} internal net(s) renamed')
if len(sys.argv) > 4:
    g = open(sys.argv[3]).read().split('\n')
    g = [renames.get(l, l) for l in g]
    open(sys.argv[4], 'w').write('\n'.join(g))
