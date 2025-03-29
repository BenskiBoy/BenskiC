from parser.Parser import *
from .TackyConstructs import *

from collections import defaultdict


class Tacky:
    def __init__(self, ast, debug) -> None:
        self.ast = ast
        self.debug = debug
        self.temp_variable_counter = 0
        self.temp_label_counter = defaultdict(int)

    def make_temporary_variable(self) -> str:
        self.temp_variable_counter += 1
        return f"tmp.{self.temp_variable_counter-1}"  # minus 1 so starts at zero

    def make_label(self, ident: str) -> str:
        self.temp_label_counter[ident] += 1
        return f"_{ident}_{str(self.temp_label_counter[ident] - 1)}_"  # minus 1 so starts at zero

    def emit_ir(self, ast: ASTNode, ir: list[IRNode] = []):

        if isinstance(ast, ConstantNode):
            return IRConstantNode(ast.value)

        elif isinstance(ast, UnaryNode):
            src = self.emit_ir(ast.children[0], ir)
            dst = IRVarNode(self.make_temporary_variable())
            tacky_op = IRUnaryOperator[ast.operator.name]

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

            if ast.operator in SHORT_CIRCUIT_BINARY_OPERATORS:

                if ast.operator == BinaryOperatorNode.AND_LOGICAL:

                    false_label = self.make_label("AND_FALSE")
                    end_label = self.make_label("AND_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.children[0], ir)
                    ir.append(IRJumpIfZeroNode(src_1, false_label))

                    src_2 = self.emit_ir(ast.children[1], ir)
                    ir.append(IRJumpIfZeroNode(src_1, false_label))
                    ir.append(IRCopyNode(IRConstantNode(1), dst))
                    ir.append(IRJumpNode(end_label))
                    ir.append(IRLabelNode(false_label))
                    ir.append(IRCopyNode(IRConstantNode(0), dst))
                    ir.append(IRLabelNode(end_label))

                elif ast.operator == BinaryOperatorNode.OR_LOGICAL:

                    true_label = self.make_label("OR_TRUE")
                    end_label = self.make_label("OR_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.children[0], ir)
                    ir.append(IRJumpIfNotZeroNode(src_1, true_label))

                    src_2 = self.emit_ir(ast.children[1], ir)
                    ir.append(IRJumpIfNotZeroNode(src_1, true_label))
                    ir.append(IRCopyNode(IRConstantNode(0), dst))
                    ir.append(IRJumpNode(end_label))
                    ir.append(IRLabelNode(true_label))
                    ir.append(IRCopyNode(IRConstantNode(1), dst))
                    ir.append(IRLabelNode(end_label))

            elif ast.operator in NON_SHORT_CIRCUIT_BINARY_OPERATORS:
                src_1 = self.emit_ir(ast.children[0], ir)
                src_2 = self.emit_ir(ast.children[1], ir)
                dst = IRVarNode(self.make_temporary_variable())
                op = IRBinaryOperator[ast.operator.name]

                ir.append(IRBinaryNode(op, src_1, src_2, dst))

            else:
                raise Exception(f"Unknown type of binary operator {ast.operator}")

            return dst

        else:
            return ir

    def pretty_print(self, instructions: list[IRNode]):
        for n in instructions:
            print(n)
