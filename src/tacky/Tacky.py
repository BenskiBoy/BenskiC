from parser.Parser import *
from .TackyConstructs import *


class Tacky:
    def __init__(self, ast, debug) -> None:
        self.ast = ast
        self.debug = debug
        self.temp_name_counter = 0

    def make_temporary(self) -> str:
        self.temp_name_counter += 1
        return f"tmp.{self.temp_name_counter-1}"

    def convert_unop(self, op: str) -> str:
        if op == UnaryOperatorNode.COMPLEMENT:
            return IRUnaryOperator.COMPLEMENT
        elif op == UnaryOperatorNode.NEGATE:
            return IRUnaryOperator.NEGATE
        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def emit_ir(self, ast: ASTNode, ir: list[IRNode] = []):

        if isinstance(ast, ConstantNode):
            return IRConstantNode(ast.value)
        elif isinstance(ast, UnaryNode):
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
            ir.append(IRProgramNode())

            for child in ast.children:
                if isinstance(child, FunctionNode):
                    content = self.emit_ir(child, ir)
            return ir

        elif isinstance(ast, FunctionNode):
            ir.append(IRFunctionNode(ast.name, ast.return_type))
            content = self.emit_ir(ast.children[0], ir)

            return ir

        elif isinstance(ast, BinaryNode):
            src_1 = self.emit_ir(ast.children[0], ir)
            src_2 = self.emit_ir(ast.children[1], ir)
            dst = IRVarNode(self.make_temporary())
            ir.append(IRBinaryNode(ast.operator, src_1, src_2, dst))
            return dst

        else:
            return ir

    def pretty_print(self, instructions: list[IRNode]):
        for n in instructions:
            print(n)
