#!/usr/bin/env python3
import argparse
import os
import sys
import re
import yaml
import pyverilog.vparser.parser as vparser
from pyverilog.vparser.ast import ModuleDef, Input, Output, Inout, Decl

def parse_verilog_ports(file_content, target_module=None):
    # Pyverilog works on files, so we first write the content to a temp file
    # (or we could just use the filename, but the parent function gives us content)
    # To keep the interface identical, we use a temp file.
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.v', delete=False) as tf:
        tf.write(file_content)
        tmp_name = tf.name
        
    try:
        ast, _ = vparser.parse([tmp_name])
    finally:
        os.unlink(tmp_name)
    
    modules = [node for node in ast.description.definitions if isinstance(node, ModuleDef)]
    if not modules:
        raise ValueError("No module found in the input file.")
        
    mod = None
    if target_module:
        for m in modules:
            if m.name == target_module:
                mod = m
                break
        if not mod:
            raise ValueError(f"Target module '{target_module}' not found in the input file.")
    else:
        mod = modules[0]
        
    ports = []
    
    # Extract ports from the AST items
    for item in mod.items:
        if isinstance(item, Decl):
            for decl in item.list:
                if isinstance(decl, (Input, Output, Inout)):
                    direction = decl.__class__.__name__.lower()
                    name = decl.name
                    width = None
                    if decl.width:
                        try:
                            # Try to extract literal bounds if possible
                            msb = decl.width.msb.value
                            lsb = decl.width.lsb.value
                            width = f"[{msb}:{lsb}]"
                        except AttributeError:
                            # Bounds might be complex expressions/parameters (e.g. PARAM-1:0)
                            # Pyverilog has string representations for these nodes
                            pass 
                    ports.append((name, direction, width))
                        
    return mod.name, ports

def get_pins(name, width):
    # Remove escaping backward slash if present for standardizing
    clean_name = name.lstrip('\\')
    
    if not width:
        return [clean_name]
        
    m = re.match(r'^\[\s*(\d+)\s*:\s*(\d+)\s*\]$', width)
    if m:
        start = int(m.group(1))
        end = int(m.group(2))
        step = -1 if start >= end else 1
        pins = []
        for val in range(start, end + step, step):
            pins.append(f"{clean_name}[{val}]")
        return pins
    else:
        # In case we couldn't parse a constant range (e.g. parameters),
        # return the base name so something is generated.
        return [clean_name]

def write_liberty(mod_name, ports, out_file, pvt_data=None):
    with open(out_file, 'w') as f:
        f.write(f"library({mod_name}_lib) {{\n")
        f.write(f"  delay_model : table_lookup;\n")
        f.write(f"  time_unit : \"1ns\";\n")
        f.write(f"  voltage_unit : \"1V\";\n")
        f.write(f"  current_unit : \"1uA\";\n")
        f.write(f"  leakage_power_unit : \"1nW\";\n")
        f.write(f"\n")
        
        if pvt_data:
            if 'operating_conditions' in pvt_data:
                for cond_name, cond_vals in pvt_data['operating_conditions'].items():
                    f.write(f"  operating_conditions({cond_name}) {{\n")
                    if 'process' in cond_vals:
                        f.write(f"    process : {cond_vals['process']} ;\n")
                    if 'temperature' in cond_vals:
                        f.write(f"    temperature : {cond_vals['temperature']} ;\n")
                    if 'voltage' in cond_vals:
                        f.write(f"    voltage : {cond_vals['voltage']} ;\n")
                    f.write(f"  }}\n")
            if 'default_operating_conditions' in pvt_data:
                f.write(f"  default_operating_conditions : {pvt_data['default_operating_conditions']} ;\n")
            f.write(f"\n")
            
        f.write(f"  cell({mod_name}) {{\n")
        f.write(f"    area : 0.0;\n")
        
        seen = set()
        for name, direction, width in ports:
            # deduplicate
            if name in seen:
                continue
            seen.add(name)
            
            pins = get_pins(name, width)
            for pin in pins:
                f.write(f"    pin(\"{pin}\") {{\n")
                f.write(f"      direction : {direction};\n")
                f.write(f"    }}\n")
                
        f.write(f"  }}\n")
        f.write(f"}}\n")

def main():
    parser = argparse.ArgumentParser(description="Convert Verilog to a basic Liberty file for linkage checking")
    parser.add_argument("--input", "--in", "-i", dest="input", required=True, help="Input Verilog file")
    parser.add_argument("--output", "--out", "-o", dest="output", help="Output Liberty file (default: <mod_name>.lib)")
    parser.add_argument("--top", "-t", help="Top module name to extract")
    parser.add_argument("--pvt", help="Optional YAML file containing PVT conditions")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
        
    pvt_data = None
    if args.pvt:
        if not os.path.exists(args.pvt):
            print(f"Error: PVT YAML file '{args.pvt}' not found.")
            sys.exit(1)
        with open(args.pvt, 'r') as yf:
            pvt_data = yaml.safe_load(yf)
        
    with open(args.input, 'r') as f:
        content = f.read()
        
    try:
        mod_name, ports = parse_verilog_ports(content, args.top)
        out_file = args.output if args.output else f"{mod_name}.lib"
        
        write_liberty(mod_name, ports, out_file, pvt_data)
        
        # Deduplication count display
        unique_ports = len(set(p[0] for p in ports))
        print(f"Successfully generated {out_file} for cell {mod_name} with {unique_ports} port definitions.")
        
    except Exception as e:
        print(f"Error parsing Verilog: {e}")
        sys.exit(1)
    finally:
        # Pyverilog generates ply artifacts parser.out and parsetab.py locally
        for junk in ('parser.out', 'parsetab.py'):
            if os.path.exists(junk):
                os.remove(junk)

if __name__ == '__main__':
    main()
