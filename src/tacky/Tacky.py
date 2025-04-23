from parser.Parser import *
from .TackyConstructs import *

from collections import defaultdict


class Tacky:
    def __init__(self, ast, debug) -> None:
        self.ast = ast
        self.debug = debug
        self.temp_variable_counter = 0
        self.temp_label_counter = defaultdict(int)

        instructions = []

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
        program_node = self.emit_ir(ast, [])
        return program_node

    def emit_ir(self, ast: ProgramNode, instructions: list[IRNode]):

        if ast is None:
            return None

        if isinstance(ast, ProgramNode):
            functions = []
            for function in ast.functions:
                func = self.emit_ir(function, [])
                if func:
                    functions.append(func)
            return IRProgramNode(functions)

        elif isinstance(ast, FunctionDeclarationNode):
            if ast.body is not None:
                self.emit_ir(ast.body, instructions)
            instructions.append(IRReturnNode(IRConstantNode(0)))
            return IRFunctionNode(ast.identifier, ast.params, instructions)

        elif isinstance(ast, BlockNode):
            for block_item in ast.children:
                self.emit_ir(block_item.child, instructions)
                # instructions.append(result)
            return None

        elif isinstance(ast, FunctionCallNode):
            args = []
            for arg in ast.arguments:
                args.append(self.emit_ir(arg, instructions))
            dst = self.make_temporary_variable()
            instructions.append(IRFunctionCallNode(ast.identifier, args, dst))
            return dst

            # return IRFunctionCallNode(ast.identifier, args, None)

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
                    src = self.emit_ir(ast.exp, instructions)
                    dst = IRVarNode(self.make_temporary_variable())
                    instructions.append(IRCopyNode(src, dst))
                    tacky_op = IRBinaryNode(
                        binary_operator_lookup[ast.operator],
                        src,
                        IRConstantNode(1),
                        src,
                    )
                    instructions.append(tacky_op)

                else:
                    src = self.emit_ir(ast.exp, instructions)
                    dst = src
                    tacky_op = IRBinaryNode(
                        binary_operator_lookup[ast.operator],
                        src,
                        IRConstantNode(1),
                        src,
                    )
                    instructions.append(tacky_op)

                return dst
            else:
                src = self.emit_ir(ast.exp, instructions)
                dst = IRVarNode(self.make_temporary_variable())
                tacky_op = IRUnaryOperator[ast.operator.name]
                instructions.append(IRUnaryNode(tacky_op, src, dst))

            return dst

        elif isinstance(ast, BinaryNode):

            if ast.operator in SHORT_CIRCUIT_BINARY_OPERATORS:

                if ast.operator == BinaryOperatorNode.AND_LOGICAL:

                    false_label = self.make_label("AND_FALSE")
                    end_label = self.make_label("AND_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.exp_1, instructions)
                    instructions.append(IRJumpIfZeroNode(src_1, false_label))

                    src_2 = self.emit_ir(ast.exp_2, instructions)
                    instructions.append(IRJumpIfZeroNode(src_2, false_label))

                    instructions.append(IRCopyNode(IRConstantNode(1), dst))
                    instructions.append(IRJumpNode(end_label))
                    instructions.append(IRLabelNode(false_label))
                    instructions.append(IRCopyNode(IRConstantNode(0), dst))
                    instructions.append(IRLabelNode(end_label))

                elif ast.operator == BinaryOperatorNode.OR_LOGICAL:

                    true_label = self.make_label("OR_TRUE")
                    end_label = self.make_label("OR_END")
                    dst = IRVarNode(self.make_temporary_variable())

                    src_1 = self.emit_ir(ast.exp_1, instructions)
                    instructions.append(IRJumpIfNotZeroNode(src_1, true_label))

                    src_2 = self.emit_ir(ast.exp_2, instructions)
                    instructions.append(IRJumpIfNotZeroNode(src_2, true_label))

                    instructions.append(IRCopyNode(IRConstantNode(0), dst))
                    instructions.append(IRJumpNode(end_label))
                    instructions.append(IRLabelNode(true_label))
                    instructions.append(IRCopyNode(IRConstantNode(1), dst))
                    instructions.append(IRLabelNode(end_label))

            elif ast.operator in NON_SHORT_CIRCUIT_BINARY_OPERATORS:
                src_1 = self.emit_ir(ast.exp_1, instructions)
                src_2 = self.emit_ir(ast.exp_2, instructions)
                dst = IRVarNode(self.make_temporary_variable())
                op = IRBinaryOperator[ast.operator.name]

                instructions.append(IRBinaryNode(op, src_1, src_2, dst))

            else:
                raise Exception(f"Unknown type of binary operator {ast.operator}")

            return dst

        elif isinstance(ast, VarNode):
            return IRVarNode(ast.identifier)

        elif isinstance(ast, AssignmentNode):
            if ast.type in ASSIGN_EQUAL_OPERATORS_LOOKUP.keys():

                src = self.emit_ir(ast.rvalue, instructions)
                dst = self.emit_ir(ast.lvalue, instructions)
                temp = IRVarNode(self.make_temporary_variable())
                tacky_op = ASSIGN_EQUAL_OPERATORS_LOOKUP[ast.type]
                instructions.append(IRBinaryNode(tacky_op, dst, src, temp))
                instructions.append(IRCopyNode(temp, dst))
                return dst

            result = self.emit_ir(ast.rvalue, instructions)
            instructions.append(IRCopyNode(result, IRVarNode(ast.lvalue.identifier)))
            return IRVarNode(ast.lvalue.identifier)

        elif isinstance(ast, DeclarationNode):
            if ast.exp:
                result = self.emit_ir(ast.exp, instructions)
                instructions.append(IRCopyNode(result, IRVarNode(ast.identifier)))
                return IRVarNode(ast.identifier)
            else:
                pass  # TODO: Nothing to do without assignment, just highlighting

        elif isinstance(ast, ReturnNode):
            if ast.exp:
                # First evaluate the expression (1 == 1)
                exp_result = self.emit_ir(ast.exp, instructions)
                # Then add a return instruction with that result
                instructions.append(IRReturnNode(exp_result))
            else:
                instructions.append(IRReturnNode(IRConstantNode(0)))
            return None  # Don't return the return node

        elif isinstance(ast, IfNode):
            false_label = self.make_label("IF_FALSE")
            end_label = self.make_label("IF_END")

            if not ast.else_:
                condition = self.emit_ir(ast.condition, instructions)
                instructions.append(IRJumpIfZeroNode(condition, end_label))
                instructions.append(self.emit_ir(ast.then, instructions))
                instructions.append(IRLabelNode(end_label))
            else:
                condition = self.emit_ir(ast.condition, instructions)
                instructions.append(IRJumpIfZeroNode(condition, false_label))
                instructions.append(self.emit_ir(ast.then, instructions))
                instructions.append(IRJumpNode(end_label))
                instructions.append(IRLabelNode(false_label))
                instructions.append(self.emit_ir(ast.else_, instructions))
                instructions.append(IRLabelNode(end_label))

        elif isinstance(ast, ConditionalNode):
            e2_label = self.make_label("CONDITIONAL_ELSE")
            end_label = self.make_label("CONDITIONAL_END")
            result_var = IRVarNode(self.make_temporary_variable())

            condition = self.emit_ir(ast.condition, instructions)
            instructions.append(IRJumpIfZeroNode(condition, e2_label))
            v1 = self.emit_ir(ast.then, instructions)
            instructions.append(IRCopyNode(v1, result_var))

            instructions.append(IRJumpNode(end_label))

            instructions.append(IRLabelNode(e2_label))
            v2 = self.emit_ir(ast.else_, instructions)
            instructions.append(IRCopyNode(v2, result_var))

            instructions.append(IRLabelNode(end_label))
            return result_var

        elif isinstance(ast, GotoNode):
            label = ast.label
            instructions.append(IRJumpNode(label))
            return None
        elif isinstance(ast, LabeledStatementNode):
            label = ast.label
            instructions.append(IRLabelNode(label))
            instructions.append(self.emit_ir(ast.child, instructions))
            return None

        elif isinstance(ast, InitDeclNode):
            if ast.declaration:
                result = self.emit_ir(ast.declaration, instructions)
                return result  # IRVarNode(ast.declaration.identifier)
            else:
                pass

        elif isinstance(ast, InitExprNode):
            if ast.expression:
                result = self.emit_ir(ast.expression, instructions)
                return result  # IRVarNode(ast.expression.identifier)
            else:
                pass

        elif isinstance(ast, BreakNode):
            instructions.append(
                IRJumpNode(self.get_control_flow_label("BREAK", ast.label))
            )
            return None
        elif isinstance(ast, ContinueNode):
            instructions.append(
                IRJumpNode(self.get_control_flow_label("CONTINUE", ast.label))
            )
            return None

        elif isinstance(ast, DoWhileNode):
            loop_label = self.get_control_flow_label("", ast.label)
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)
            condition_result_var = IRVarNode(self.make_temporary_variable())

            instructions.append(IRLabelNode(loop_label))
            self.emit_ir(ast.body, instructions)

            instructions.append(IRLabelNode(continue_label))
            condition = self.emit_ir(ast.condition, instructions)
            instructions.append(IRCopyNode(condition, condition_result_var))
            instructions.append(IRJumpIfNotZeroNode(condition_result_var, loop_label))
            instructions.append(IRLabelNode(break_label))

        elif isinstance(ast, WhileNode):
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)
            condition_result_var = IRVarNode(self.make_temporary_variable())

            instructions.append(IRLabelNode(continue_label))

            condition = self.emit_ir(ast.condition, instructions)
            instructions.append(IRCopyNode(condition, condition_result_var))
            instructions.append(IRJumpIfZeroNode(condition_result_var, break_label))
            self.emit_ir(ast.body, instructions)

            instructions.append(IRJumpNode(continue_label))
            instructions.append(IRLabelNode(break_label))

        elif isinstance(ast, ForNode):
            loop_label = self.get_control_flow_label("", ast.label)
            break_label = self.get_control_flow_label("BREAK", ast.label)
            continue_label = self.get_control_flow_label("CONTINUE", ast.label)

            condition_result_var = IRVarNode(self.make_temporary_variable())

            if ast.init:
                self.emit_ir(ast.init, instructions)
            instructions.append(IRLabelNode(loop_label))

            if ast.condition:
                condition = self.emit_ir(ast.condition, instructions)
                instructions.append(IRCopyNode(condition, condition_result_var))
                instructions.append(IRJumpIfZeroNode(condition_result_var, break_label))
            self.emit_ir(ast.body, instructions)

            instructions.append(IRLabelNode(continue_label))
            self.emit_ir(ast.post, instructions)
            instructions.append(IRJumpNode(loop_label))
            instructions.append(IRLabelNode(break_label))

        elif isinstance(ast, CaseNode):
            if not hasattr(ast, "label") or not ast.label:
                raise AttributeError("CaseNode missing 'label' attribute")

            instructions.append(IRLabelNode(ast.label))
            for item in ast.body:
                instructions.append(self.emit_ir(item, instructions))

            return None

        elif isinstance(ast, DefaultNode):
            if not hasattr(ast, "label") or not ast.label:
                raise AttributeError("DefaultNode missing 'label' attribute")

            instructions.append(IRLabelNode(ast.label))
            for item in ast.body:
                instructions.append(self.emit_ir(item, instructions))
            return None

        elif isinstance(ast, SwitchNode):
            # Ensure required attributes exist
            if not hasattr(ast, "label"):
                raise AttributeError("SwitchNode missing 'label' attribute")
            if not hasattr(ast, "case_targets"):
                raise AttributeError("SwitchNode missing 'case_targets' attribute")

            switch_end_label = f"{ast.label}_END"
            switch_break_label = self.get_control_flow_label("BREAK", ast.label)

            condition_value = self.emit_ir(ast.condition, instructions)

            if not isinstance(condition_value, (IRVarNode, IRConstantNode)):
                temp_var = IRVarNode(self.make_temporary_variable())
                instructions.append(IRCopyNode(condition_value, temp_var))
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
                    case_value = self.emit_ir(case_node.condition, instructions)

                    # Compare: switch_condition == case_value
                    cmp_result = IRVarNode(self.make_temporary_variable())
                    instructions.append(
                        IRBinaryNode(
                            IRBinaryOperator.EQUAL,
                            condition_value,
                            case_value,
                            cmp_result,
                        )
                    )

                    instructions.append(IRJumpIfNotZeroNode(cmp_result, case_label))

            if ast.default_target:
                instructions.append(IRJumpNode(ast.default_target))
            else:
                instructions.append(IRJumpNode(switch_end_label))

            self.emit_ir(ast.body, instructions)

            instructions.append(IRLabelNode(switch_end_label))
            instructions.append(IRLabelNode(switch_break_label))

            return None

    def pretty_print(self, prog_node: IRProgramNode):
        for func in prog_node.function_definitions:
            print(func)
            for instr in func.body:
                print(instr)
