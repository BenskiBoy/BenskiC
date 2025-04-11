from parser.ParserConstructs import *
from collections import defaultdict


class SemanticAnalysis:
    def __init__(self):
        self.variable_map = defaultdict(int)
        self.original_variable_names = []
        self.label_declarations = []
        self.label_calls = []

    def make_temporary_identifier(self, identifier: str) -> str:
        if identifier not in self.variable_map:
            self.variable_map[identifier] = 0
            self.original_variable_names.append(identifier)
            return f"{identifier}.{str(self.variable_map[identifier])}"
        else:
            # increment the variable map for the identifier
            self.variable_map[identifier] += 1
            return f"{identifier}.{str(self.variable_map[identifier] - 1)}"  # minus 1 so starts at zero

    def get_temporary_identifier(self, identifier: str) -> str:
        if identifier in self.variable_map:
            return f"{identifier}.{str(self.variable_map[identifier])}"
        else:
            raise Exception(f"Temporary identifier '{identifier}' not found.")

    def parse(self, ast: ProgramNode) -> ProgramNode:

        if isinstance(ast, ProgramNode):
            for i, function in enumerate(ast.functions):
                if isinstance(function, FunctionNode):
                    ast.functions[0] = self.parse(function)

        elif isinstance(ast, FunctionNode):
            for i, child in enumerate(ast.block_items):
                for j, block_item in enumerate(child):
                    res = self.parse_block_item(block_item)
                    ast.block_items[i][j] = res

        if self.label_calls:  # check if there are any label calls
            if not bool(set(self.label_declarations) & set(self.label_calls)):
                raise Exception(
                    f"Label name '{set(self.label_declarations) & set(self.label_calls)}' not declared."
                )

        return ast

    def parse_block_item(self, block: BlockItemNode) -> BlockItemNode:

        content = block.child
        if isinstance(content, DeclarationNode):
            return BlockItemNode(self.resolve_declaration(content))
        elif (
            isinstance(content, ReturnNode)
            or isinstance(block, ExpressionNode)
            or isinstance(content, IfNode)
            or isinstance(content, LabeledStatementNode)
        ):  # statement
            return BlockItemNode(self.resolve_statement(content))
        elif isinstance(content, ExpressionNode):
            return BlockItemNode(self.resolve_expression(content))
        elif content is None:
            return BlockItemNode(None)
        elif isinstance(content, GotoNode):
            self.label_calls.append(content.label)
            return BlockItemNode(content)
        else:
            raise Exception(f"Unknown block item type {content}.")

    def resolve_declaration(self, declaration: DeclarationNode) -> DeclarationNode:
        if declaration.identifier in self.variable_map:
            raise Exception(f"Variable '{declaration.identifier}' already declared.")

        unique_name = self.make_temporary_identifier(declaration.identifier)
        if declaration.exp is not None:
            expression = self.resolve_expression(declaration.exp)
        else:
            expression = None

        return DeclarationNode(
            unique_name,
            expression,
        )

    def resolve_statement(self, statement: Statement) -> Statement:
        if isinstance(statement, ReturnNode):
            return ReturnNode(self.resolve_expression(statement.exp))

        elif isinstance(statement, LabeledStatementNode):
            label = statement.label
            if statement.label in self.label_declarations:
                raise Exception(f"Label '{statement.label}' already called.")
            self.label_declarations.append(statement.label)
            return LabeledStatementNode(
                label,
                self.resolve_statement(statement.child),
            )

        elif isinstance(statement, IfNode):
            condition = self.resolve_expression(statement.condition)
            then = self.resolve_statement(statement.then)
            else_ = (
                self.resolve_statement(statement.else_)
                if statement.else_ is not None
                else None
            )
            return IfNode(condition, then, else_)
        elif isinstance(statement, AssignmentNode):
            if self.resolve_expression(statement.rvalue) in self.label_declarations:
                raise Exception(
                    f"Label '{expression.rvalue.identifier}' cannot be used as an expression."
                )
            return AssignmentNode(
                self.resolve_expression(statement.lvalue),
                self.resolve_expression(statement.rvalue),
                statement.type,
            )
        elif isinstance(statement, GotoNode):
            self.label_calls.append(statement.label)
            return GotoNode(statement.label)

        elif statement is None:
            return None

        elif isinstance(statement.child, ExpressionNode):
            expression = self.resolve_expression(statement.child)
            return expression

        else:
            raise Exception(f"Unknown statement type {type(statement)}.")

    def resolve_expression(self, expression: ExpressionNode) -> ExpressionNode:

        print(f"resolving expression {repr(expression)}")
        if isinstance(expression, VarNode):
            if expression.identifier in self.variable_map:
                return VarNode(self.get_temporary_identifier(expression.identifier))
            else:
                raise Exception(f"Variable '{expression.identifier}' not declared.")
        elif isinstance(
            expression,
            AssignmentNode,
        ):
            if not isinstance(expression.lvalue, VarNode):
                raise Exception("Left side of assignment must be a variable.")
            return AssignmentNode(
                self.resolve_expression(expression.lvalue),
                self.resolve_expression(expression.rvalue),
                expression.type,
            )
        elif isinstance(expression, BinaryNode):
            left = self.resolve_expression(expression.exp_1)
            right = self.resolve_expression(expression.exp_2)
            return BinaryNode(
                expression.operator,
                left,
                right,
            )
        elif isinstance(expression, UnaryNode):
            child = self.resolve_expression(expression.exp)

            if isinstance(child, UnaryNode) and isinstance(expression, UnaryNode):
                if expression.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ] and child.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ]:
                    raise Exception(
                        "Increment/Decrement operator cannot be used on itself."
                    )
            if isinstance(child, AssignmentNode) and isinstance(
                expression.operator, UnaryOperatorNode
            ):
                raise Exception("Unary operator cannot be used on assignment.")
            if isinstance(child, (ConstantNode, BinaryNode)) and isinstance(
                expression, UnaryNode
            ):
                if expression.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ]:
                    raise Exception(
                        "Unary operator cannot be used on constant or binary node."
                    )
            return UnaryNode(child, expression.operator, expression.postfix)

        elif isinstance(expression, ConditionalNode):
            condition = self.resolve_expression(expression.condition)
            true_exp = self.resolve_expression(expression.then)
            false_exp = self.resolve_expression(expression.else_)
            return ConditionalNode(condition, true_exp, false_exp)

        else:
            return expression

    def pretty_print(self, ast):
        print(self.variable_map)

        for function in ast.functions:
            print(function.__str__())
            for block in function.block_items:
                for item in block:
                    print(repr(item))
