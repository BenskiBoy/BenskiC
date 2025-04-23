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

    def get_control_flow_label(self, prefix, node_label):
        """Generate a consistent control flow label"""
        # Extract just the important parts from node_label (e.g., "FOR_LOOP_1")
        parts = node_label.strip("_").split("_")
        if len(parts) >= 3:
            # Extract type and number: "FOR", "LOOP", "1"
            type_part = parts[-3]  # "FOR"
            number_part = parts[-1]  # "1"
            return f"_{prefix}_{type_part}_LOOP_{number_part}_"
        else:
            # Fallback for any other format
            return f"_{prefix}_{node_label}_"

    def parse(self, ast) -> list[IRNode]:
        self.emit_ir(self.ast)

        self.ir.append(IRProgramNode())

        for function in ast.functions:
            self.ir.append(IRFunctionNode(function.identifier, function.return_type))
            self.emit_ir(function.body)
            self.ir.append(
                IRReturnNode(IRConstantNode(0))
            )  # for the case of no return, if there is a return at the end, this will never be called

        return self.ir

    def emit_ir(self, ast: ProgramNode):

        if ast is None:
            return None

        elif isinstance(ast, BlockNode):
            for block_item in ast.children:
                if isinstance(block_item.child, ReturnNode):
                    res = self.emit_ir(block_item.child.exp)
                    self.ir.append(IRReturnNode(res))
                else:
                    self.emit_ir(block_item.child)

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

        elif isinstance(ast, InitDeclNode):
            if ast.declaration:
                result = self.emit_ir(ast.declaration)
                return result  # IRVarNode(ast.declaration.identifier)
            else:
                pass

        elif isinstance(ast, InitExprNode):
            if ast.expression:
                result = self.emit_ir(ast.expression)
                return result  # IRVarNode(ast.expression.identifier)
            else:
                pass

        elif isinstance(ast, BreakNode):
            self.ir.append(IRJumpNode(self.get_control_flow_label("BREAK", ast.label)))
            return None
        elif isinstance(ast, ContinueNode):
            self.ir.append(
                IRJumpNode(self.get_control_flow_label("CONTINUE", ast.label))
            )
            return None

        elif isinstance(ast, DoWhileNode):
            loop_label = self.get_control_flow_label("", ast.label)
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)
            condition_result_var = IRVarNode(self.make_temporary_variable())

            self.ir.append(IRLabelNode(loop_label))
            self.emit_ir(ast.body)

            self.ir.append(IRLabelNode(continue_label))
            condition = self.emit_ir(ast.condition)
            self.ir.append(IRCopyNode(condition, condition_result_var))
            self.ir.append(IRJumpIfNotZeroNode(condition_result_var, loop_label))
            self.ir.append(IRLabelNode(break_label))

        elif isinstance(ast, WhileNode):
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)
            condition_result_var = IRVarNode(self.make_temporary_variable())

            self.ir.append(IRLabelNode(continue_label))

            condition = self.emit_ir(ast.condition)
            self.ir.append(IRCopyNode(condition, condition_result_var))
            self.ir.append(IRJumpIfZeroNode(condition_result_var, break_label))
            self.emit_ir(ast.body)

            self.ir.append(IRJumpNode(continue_label))
            self.ir.append(IRLabelNode(break_label))

        elif isinstance(ast, ForNode):
            loop_label = self.get_control_flow_label("", ast.label)
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)

            condition_result_var = IRVarNode(self.make_temporary_variable())

            if ast.init:
                self.emit_ir(ast.init)
            self.ir.append(IRLabelNode(loop_label))

            if ast.condition:
                condition = self.emit_ir(ast.condition)
                self.ir.append(IRCopyNode(condition, condition_result_var))
                self.ir.append(IRJumpIfZeroNode(condition_result_var, break_label))
            self.emit_ir(ast.body)

            self.ir.append(IRLabelNode(continue_label))
            self.emit_ir(ast.post)
            self.ir.append(IRJumpNode(loop_label))
            self.ir.append(IRLabelNode(break_label))

        elif isinstance(ast, CaseNode):
            if not hasattr(ast, "label") or not ast.label:
                raise AttributeError("CaseNode missing 'label' attribute")

            self.ir.append(IRLabelNode(ast.label))
            for item in ast.body:
                self.ir.append(self.emit_ir(item))

            return None

        elif isinstance(ast, DefaultNode):
            if not hasattr(ast, "label") or not ast.label:
                raise AttributeError("DefaultNode missing 'label' attribute")

            self.ir.append(IRLabelNode(ast.label))
            for item in ast.body:
                self.ir.append(self.emit_ir(item))
            return None

        elif isinstance(ast, SwitchNode):
            # Ensure required attributes exist
            if not hasattr(ast, "label"):
                raise AttributeError("SwitchNode missing 'label' attribute")
            if not hasattr(ast, "case_targets"):
                raise AttributeError("SwitchNode missing 'case_targets' attribute")

            switch_end_label = f"{ast.label}_END"
            switch_break_label = self.get_control_flow_label("BREAK", ast.label)

            condition_value = self.emit_ir(ast.condition)

            if not isinstance(condition_value, (IRVarNode, IRConstantNode)):
                temp_var = IRVarNode(self.make_temporary_variable())
                self.ir.append(IRCopyNode(condition_value, temp_var))
                condition_value = temp_var

            case_nodes = {}  # Maps label -> CaseNode
            default_node = None

            # Function to recursively find case/default nodes in the switch body
            def find_case_nodes(node):
                if node is None:
                    return

                # First check if this node itself is a case or default
                if isinstance(node, CaseNode):
                    case_nodes[node.label] = node
                    for item in node.body:
                        find_case_nodes(item)
                elif isinstance(node, DefaultNode):
                    nonlocal default_node
                    default_node = node
                    for item in node.body:
                        find_case_nodes(item)
                elif isinstance(node, BlockNode):
                    for item in node.children:
                        find_case_nodes(item)
                elif isinstance(node, BlockItemNode):
                    find_case_nodes(node.child)
                elif isinstance(node, DoWhileNode):
                    find_case_nodes(node.body)
                elif isinstance(node, WhileNode):
                    find_case_nodes(node.body)
                elif isinstance(node, ForNode):
                    find_case_nodes(node.body)
                elif isinstance(node, IfNode):
                    find_case_nodes(node.then)
                    if node.else_:
                        find_case_nodes(node.else_)

            find_case_nodes(ast.body)

            for case_label in ast.case_targets:
                if case_label in case_nodes:
                    case_node = case_nodes[case_label]
                    case_value = self.emit_ir(case_node.condition)

                    # Compare: switch_condition == case_value
                    cmp_result = IRVarNode(self.make_temporary_variable())
                    self.ir.append(
                        IRBinaryNode(
                            IRBinaryOperator.EQUAL,
                            condition_value,
                            case_value,
                            cmp_result,
                        )
                    )

                    self.ir.append(IRJumpIfNotZeroNode(cmp_result, case_label))

            if ast.default_target:
                self.ir.append(IRJumpNode(ast.default_target))
            else:
                self.ir.append(IRJumpNode(switch_end_label))

            self.emit_ir(ast.body)

            self.ir.append(IRLabelNode(switch_end_label))
            self.ir.append(IRLabelNode(switch_break_label))

            return None

    def pretty_print(self, instructions: list[IRNode]):
        for n in instructions:
            print(n)
