# boson-synthesis

Logic synthesis and technology mapping with **partcl's boson**, as an mflowgen tool. It is a drop-in
alternative to `open-yosys-synthesis` / `cadence-genus-synthesis` / `synopsys-dc-synthesis`: it reads
the design RTL and the ADK standard cells and produces a gate netlist mapped to the ADK.

## Inputs / outputs

| direction | name | what |
|---|---|---|
| input | `adk` | the ASIC design kit (`stdcells.lib`, `rtk-tech.lef`, `stdcells.lef`, `adk.tcl`) |
| input | `design.v` | the design RTL |
| output | `design.v` | the mapped gate netlist |
| output | `synth.stats.txt` | boson QoR summary |

## Parameters

| parameter | default | meaning |
|---|---|---|
| `design_name` | `undefined` | top module |
| `clock_period` | `2.0` | clock period (ns) the synthesis SDC constrains |
| `clock_port` | `clk` | top-level clock port |
| `boson_bin` | `boson` | path to (or name on `$PATH` of) the boson binary |
| `effort` | `high` | boson compile effort |

## How it works

`boson-synth.tcl` reads the ADK liberty/LEF, sources `adk.tcl` for the cell names, writes a synthesis
SDC from the parameters, runs `compile`, and writes the mapped netlist. boson reads its parameters from
the environment (which mflowgen populates), so no script-generation pass is needed. `busify.py` then
normalizes the netlist for downstream place-and-route: boson emits top-level bus bits as escaped scalar
ports (`\name[i] `), which busify turns into real vector ports (`name[i]`), and bracketed escaped
internal net names become bracket-free. Constant tie-offs are resolved to the ADK tie cells
(`ADK_TIE_HI_CELL`/`ADK_TIE_LO_CELL`) when the ADK names them.

## Status

Validated against the bundled `freepdk-45nm` ADK on the `GcdUnit` demo design: boson maps the RTL to
the ADK's cells (BUF_X1, INV_X1, DFF_X1, MUX2_X1, …) and busify normalizes the interface.

boson is a synthesis tool from partcl (https://partcl.com); this step invokes it through its
command-line/TCL interface and does not include boson itself.
