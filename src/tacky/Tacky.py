from parser.Parser import *
from .TackyConstructs import *

from collections import defaultdict


class Tacky:
    def __init__(self, ast, debug) -> None:
        self.ast = ast
        self.debug = debug
        self.temp_variable_counter = 0
        self.temp_label_counter = defaultdict(int)

        self.ir = []

    def make_temporary_variable(self) -> str:
        self.temp_variable_counter += 1
        return f"tmp.{self.temp_variable_counter-1}"  # minus 1 so starts at zero

    def make_label(self, ident: str) -> str:
        self.temp_label_counter[ident] += 1
        return f"_{ident}_{str(self.temp_label_counter[ident] - 1)}_"  # minus 1 so starts at zero

    def parse(self, ast) -> list[IRNode]:
        self.emit_ir(self.ast)

        self.ir.append(IRProgramNode())

        for function in ast.functions:
            self.ir.append(IRFunctionNode(function.name, function.return_type))
            for block in function.block_items:
                for item in block:
                    if isinstance(item.child, ReturnNode):
                        res = self.emit_ir(item.child.exp)
                        self.ir.append(IRReturnNode(res))
                    else:
                        res = self.emit_ir(item.child)
            self.ir.append(
                IRReturnNode(IRConstantNode(0))
            )  # for the case of no return, if there is a return at the end, this will never be called

        return self.ir

    def emit_ir(self, ast: ProgramNode):

        if ast is None:
            return None

        elif isinstance(ast, ConstantNode):
            return IRConstantNode(ast.value)

        elif isinstance(ast, UnaryNode):

            if ast.operator in [
                UnaryOperatorNode.INCREMENT,
                UnaryOperatorNode.DECREMENT,
            ]:
                binary_operator_lookup = {
                    UnaryOperatorNode.INCREMENT: IRBinaryOperator.ADD,
                    UnaryOperatorNode.DECREMENT: IRBinaryOperator.SUBTRACT,
                }
                if ast.postfix:
                    src = self.emit_ir(ast.exp)
                    dst = IRVarNode(self.make_temporary_variable())
                    self.ir.append(IRCopyNode(src, dst))
                    tacky_op = IRBinaryNode(
                        binary_operator_lookup[ast.operator],
                        src,
                        IRConstantNode(1),
                        src,
                    )
                    self.ir.append(tacky_op)

                else:
                    src = self.emit_ir(ast.exp)
                    dst = src
                    tacky_op = IRBinaryNode(
                        binary_operator_lookup[ast.operator],
                        src,
                        IRConstantNode(1),
                        src,
                    )
                    self.ir.append(tacky_op)

                return dst
            else:
                src = self.emit_ir(ast.exp)
                dst = IRVarNode(self.make_temporary_variable())
                tacky_op = IRUnaryOperator[ast.operator.name]
                self.ir.append(IRUnaryNode(tacky_op, src, dst))

            return dst

        elif isinstance(ast, BinaryNode):

            if ast.operator in SHORT_CIRCUIT_BINARY_OPERATORS:

                if ast.operator == BinaryOperatorNode.AND_LOGICAL:

                    false_label = self.make_label("AND_FALSE")
                    end_label = self.make_label("AND_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.exp_1)
                    self.ir.append(IRJumpIfZeroNode(src_1, false_label))

                    src_2 = self.emit_ir(ast.exp_2)
                    self.ir.append(IRJumpIfZeroNode(src_2, false_label))

                    self.ir.append(IRCopyNode(IRConstantNode(1), dst))
                    self.ir.append(IRJumpNode(end_label))
                    self.ir.append(IRLabelNode(false_label))
                    self.ir.append(IRCopyNode(IRConstantNode(0), dst))
                    self.ir.append(IRLabelNode(end_label))

                elif ast.operator == BinaryOperatorNode.OR_LOGICAL:

                    true_label = self.make_label("OR_TRUE")
                    end_label = self.make_label("OR_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.exp_1)
                    self.ir.append(IRJumpIfNotZeroNode(src_1, true_label))

                    src_2 = self.emit_ir(ast.exp_2)
                    self.ir.append(IRJumpIfNotZeroNode(src_2, true_label))

                    self.ir.append(IRCopyNode(IRConstantNode(0), dst))
                    self.ir.append(IRJumpNode(end_label))
                    self.ir.append(IRLabelNode(true_label))
                    self.ir.append(IRCopyNode(IRConstantNode(1), dst))
                    self.ir.append(IRLabelNode(end_label))

            elif ast.operator in NON_SHORT_CIRCUIT_BINARY_OPERATORS:
                src_1 = self.emit_ir(ast.exp_1)
                src_2 = self.emit_ir(ast.exp_2)
                dst = IRVarNode(self.make_temporary_variable())
                op = IRBinaryOperator[ast.operator.name]

                self.ir.append(IRBinaryNode(op, src_1, src_2, dst))

            else:
                raise Exception(f"Unknown type of binary operator {ast.operator}")

            return dst

        elif isinstance(ast, VarNode):
            return IRVarNode(ast.identifier)

        elif isinstance(ast, AssignmentNode):
            if ast.type in ASSIGN_EQUAL_OPERATORS_LOOKUP.keys():

                src = self.emit_ir(ast.rvalue)
                dst = self.emit_ir(ast.lvalue)
                temp = IRVarNode(self.make_temporary_variable())
                tacky_op = ASSIGN_EQUAL_OPERATORS_LOOKUP[ast.type]
                self.ir.append(IRBinaryNode(tacky_op, dst, src, temp))
                self.ir.append(IRCopyNode(temp, dst))
                return dst

            result = self.emit_ir(ast.rvalue)
            self.ir.append(IRCopyNode(result, IRVarNode(ast.lvalue.identifier)))
            return IRVarNode(ast.lvalue.identifier)

        elif isinstance(ast, DeclarationNode):
            if ast.exp:
                result = self.emit_ir(ast.exp)
                self.ir.append(IRCopyNode(result, IRVarNode(ast.identifier)))
                return IRVarNode(ast.identifier)
            else:
                pass  # TODO: Nothing to do without assignment, just highlighting

        elif isinstance(ast, ReturnNode):
            if ast.exp:
                result = IRReturnNode(self.emit_ir(ast.exp))
                return result
            else:
                return IRConstantNode(0)

        elif isinstance(ast, IfNode):
            false_label = self.make_label("IF_FALSE")
            end_label = self.make_label("IF_END")

            if not ast.else_:
                condition = self.emit_ir(ast.condition)
                self.ir.append(IRJumpIfZeroNode(condition, end_label))
                self.ir.append(self.emit_ir(ast.then))
                self.ir.append(IRLabelNode(end_label))
            else:
                condition = self.emit_ir(ast.condition)
                self.ir.append(IRJumpIfZeroNode(condition, false_label))
                self.ir.append(self.emit_ir(ast.then))
                self.ir.append(IRJumpNode(end_label))
                self.ir.append(IRLabelNode(false_label))
                self.ir.append(self.emit_ir(ast.else_))
                self.ir.append(IRLabelNode(end_label))

        elif isinstance(ast, ConditionalNode):
            e2_label = self.make_label("CONDITIONAL_ELSE")
            end_label = self.make_label("CONDITIONAL_END")
            result_var = IRVarNode(self.make_temporary_variable())

            condition = self.emit_ir(ast.condition)
            self.ir.append(IRJumpIfZeroNode(condition, e2_label))
            v1 = self.emit_ir(ast.then)
            self.ir.append(IRCopyNode(v1, result_var))

            self.ir.append(IRJumpNode(end_label))

            self.ir.append(IRLabelNode(e2_label))
            v2 = self.emit_ir(ast.else_)
            self.ir.append(IRCopyNode(v2, result_var))

            self.ir.append(IRLabelNode(end_label))
            return result_var

        elif isinstance(ast, GotoNode):
            label = ast.label
            self.ir.append(IRJumpNode(label))
            return None
        elif isinstance(ast, LabeledStatementNode):
            label = ast.label
            self.ir.append(IRLabelNode(label))
            self.ir.append(self.emit_ir(ast.child))
            return None

    def pretty_print(self, instructions: list[IRNode]):
        for n in instructions:
            print(n)
