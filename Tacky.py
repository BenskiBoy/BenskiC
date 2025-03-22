from Parser import *


class IRNode:
    def __init__(self, op: str, src: ["IRNode"], dst: ["IRNode"]) -> None:
        self.op = op
        self.src = src
        self.dst = dst

    def __str__(self) -> str:
        return f"""IRNode({self.op}, {self.src}, {self.dst})"""


class IRConstantNode(IRNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", None, None)
        self.value = value

    def __str__(self) -> str:
        return f"""IRConstantNode({self.value})"""

    def __repr__(self) -> str:
        return f"""IRConstantNode({self.value})"""


class IRUnaryNode(IRNode):
    def __init__(self, op: str, src: IRNode, dst: IRNode) -> None:
        super().__init__(op, src, dst)

    def __str__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.src}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.src}, {self.dst})"""


class IRVarNode(IRNode):
    def __init__(self, name: str) -> None:
        super().__init__("VAR", name, None)

    def __str__(self) -> str:
        return f"""IRVarNode({self.src})"""

    def __repr__(self) -> str:
        return f"""IRVarNode({self.src})"""


class IRReturnNode(IRNode):
    def __init__(self, val: IRNode) -> None:
        super().__init__("RETURN", val, None)

    def __str__(self) -> str:
        return f"""IRReturnNode({self.src})"""

    def __repr__(self) -> str:
        return f"""IRReturnNode({self.src})"""


class Tacky:
    def __init__(self, ast, debug) -> None:
        self.ast = ast
        self.debug = debug
        self.temp_name_counter = 0

    def make_temporary(self) -> str:
        self.temp_name_counter += 1
        return f"tmp.{self.temp_name_counter-1}"

    def convert_unop(self, op: str) -> str:
        if op == "~":
            return "COMPLEMENT"
        elif op == "-":
            return "NEGATE"

    def emit_ir(self, ast: ASTNode, ir: list[IRNode] = []):

        if ast.type == "CONSTANT":
            return IRConstantNode(ast.value)
        elif ast.type == "UNARY":
            src = self.emit_ir(ast.children[0], ir)
            dst = IRVarNode(self.make_temporary())
            tacky_op = self.convert_unop(ast.operator)
            ir.append(IRUnaryNode(tacky_op, src, dst))
            return dst

        elif isinstance(ast, ReturnNode):
            content = self.emit_ir(ast.children[0], ir)
            ir.append(IRReturnNode(content))

            return ir

        elif isinstance(ast, ProgramNode):
            return self.emit_ir(ast.children[0], ir)

        elif isinstance(ast, FunctionNode):
            return self.emit_ir(ast.children[0], ir)

        else:
            return ir

    def pretty_print(self, instructions: list[IRNode]):
        for n in instructions:
            print(n)
