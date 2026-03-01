import sys
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import ModuleDef, Input, Output, Inout, Decl

def test_parse(file_path):
    ast, directives = parse([file_path])
    
    modules = [node for node in ast.description.definitions if isinstance(node, ModuleDef)]
    for mod in modules:
        print(f"Module: {mod.name}")
        ports = []
        for item in mod.items:
            if isinstance(item, Decl):
                for decl in item.list:
                    if isinstance(decl, (Input, Output, Inout)):
                        direction = decl.__class__.__name__.lower()
                        name = decl.name
                        width = None
                        if decl.width:
                            msb = decl.width.msb.value
                            lsb = decl.width.lsb.value
                            width = f"[{msb}:{lsb}]"
                        ports.append((name, direction, width))
        print(f"Ports: {len(ports)}")
        for x in ports[:5]:
            print("  ", x)
            
if __name__ == '__main__':
    test_parse(sys.argv[1])
