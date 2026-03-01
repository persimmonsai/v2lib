# v2lib

`v2lib` is a Verilog to Liberty (.lib) linkage converter. 

It uses [Pyverilog](https://github.com/PyHDI/Pyverilog) to natively parse the Abstract Syntax Tree (AST) of a Verilog gate-level netlist or RTL file and generate a purely structural, timing-less Liberty file (`.lib`) containing port interfaces and configurable PVT mapping conditions. 

This enables validation of structural block linkage against synthesized libraries early in the ASIC/FPGA digital design flow.

## Features

- **Robust AST Parsing**: Safely handles complex module parameterizations, attributes, block/line comments, and vector dimensions (e.g., `[31:0]`).
- **PVT Configurations**: Dynamically ingest custom Operating Conditions (Process, Voltage, Temperature) from a simple `pvt.yaml` file to embed into the library structure.
- **Port Expansion**: Automatically iterates and fully expands all single-wire and vector bus ranges for accurate `.lib` pin assignments.
- **Containerized**: Fully integrated as a rootless Docker container so you don't need to pollute your host system with `iverilog` or Python dependencies.
- **GitHub Packages**: An automated CI flow pushes the container to `ghcr.io` for zero-setup usage.

## Requirements 

*If running natively without Docker:*
- Python 3.9+
- [Icarus Verilog (`iverilog`)](https://github.com/steveicarus/iverilog) (required by Pyverilog's preprocessor)
- `pyverilog`
- `pyyaml`

## Usage (Docker Wrapper)

The easiest way to run the script is using the provided Docker wrapper script `v2lib-docker.sh`. It automatically handles volume mounting for relative and absolute paths in your workspace.

```bash
# Basic usage
./v2lib-docker.sh --in layout.v --out layout.lib

# Specify a top module and inject YAML-based PVT conditions
./v2lib-docker.sh --in /path/to/design.v \
                  --out /path/to/design.lib \
                  --top my_top_module \
                  --pvt /path/to/pvt.yaml
```

## `pvt.yaml` Format

If you would like to include library-specific process, voltage, and temperature combinations, create a YAML file mimicking this structure:

```yaml
default_operating_conditions: tt_0p7500v_85c
operating_conditions:
  tt_0p7500v_85c:
    process: 1
    temperature: 85
    voltage: 0.75
  ff_0p8250v_125c:
    process: 0.8
    temperature: 125
    voltage: 0.825
```
