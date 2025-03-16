from Parser import *

from collections import defaultdict


class AssemblyNode:
    def __init__(self, command: str, *args) -> None:
        self.command = command
        self.args = [arg for arg in args if arg != None]

    def __str__(self) -> str:
        return f"{self.command} {', '.join(str(arg) for arg in self.args)}".strip()


class MovAsmNode(AssemblyNode):
    def __init__(self, arg1=None, arg2=None) -> None:
        super().__init__("movl", arg1, arg2)

    def add_arg(self, arg):
        self.args.append(arg)


class RetAsmNode(AssemblyNode):
    def __init__(self, arg=None) -> None:
        super().__init__("ret", arg)


class ImmAsmNode(AssemblyNode):
    def __init__(self, arg=None) -> None:
        super().__init__("IMM", arg)

    def add_arg(self, arg):
        self.args.append(arg)


class AssemblyParser:

    def __init__(self) -> None:
        self.globals = []
        self.types = []
        self.instructions = []

    def parse_function(self, ast: FunctionNode) -> AssemblyNode:
        self.globals.append(AssemblyNode(f".global", ast.name))
        self.types.append(AssemblyNode(".type", ast.name, "@function"))

        self.instructions.append(AssemblyNode(ast.name + ":", ""))

    def parse_return(self, ast: ASTNode):
        self.instructions.append(MovAsmNode("$" + ast.children[0].value, "%eax"))
        self.instructions.append(RetAsmNode())

    def parse_program(self, ast: ASTNode):
        pass
        # for child in ast.children:
        #     self.assembly.append(get_asm_node(child))
        #     self.parse_program(child)

    def parse_constant(self, ast: ConstantNode):
        pass


ASSEMBLY_NODE_LOOKUP = {
    ReturnNode: lambda self, node: self.parse_return(node),
    # ConstantNode: lambda self, node: self.parse_constant(node),
    FunctionNode: lambda self, node: self.parse_function(node),
    ProgramNode: lambda self, node: self.parse_program(node),
    ConstantNode: lambda self, node: self.parse_program(node),
}


class AsmParser:
    def __init__(self, ast, input_file_name, debug) -> None:
        self.ast = ast
        self.assembly_parser = AssemblyParser()
        self.input_file_name = input_file_name
        self.debug = debug

    def parse(self) -> list[str]:

        def _parse(ast):

            for child in ast.children:
                ASSEMBLY_NODE_LOOKUP[child.__class__](self.assembly_parser, child)
                if len(child.children) > 0:
                    _parse(child)

        _parse(self.ast)

        return self.assembly_parser.instructions

    def generate(self):

        content = ""

        content += f'  .file "{self.input_file_name}"\n'
        content += f"  .text\n"

        for glob in self.assembly_parser.globals:
            content += f"  .global {glob.args[0]}\n"

        for typ in self.assembly_parser.types:
            content += f"  .type {typ.args[0]}, {typ.args[1]}\n"

        for inst in self.assembly_parser.instructions:
            if str(inst)[-1] == ":":
                content += str(inst) + "\n"
            else:
                content += f"  {str(inst)}" + "\n"

        content += f'  .ident  "GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0"\n'
        content += f'  .section  .note.GNU-stack,"",@progbits\n'

        return content
