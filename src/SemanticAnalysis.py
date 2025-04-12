from parser.ParserConstructs import *
from collections import defaultdict


class SemanticAnalysis:
    def __init__(self):
        self.variable_scopes = [
            {}
        ]  # Stack of scopes - each is a dict mapping original names to unique names
        self.scope_level = 0
        self.all_declarations = (
            set()
        )  # Track all declarations across all scopes for error reporting
        self.original_variable_names = []
        self.label_declarations = []
        self.label_calls = []

    def enter_scope(self):
        """Create a new variable scope when entering a block."""
        self.variable_scopes.append({})
        self.scope_level += 1

    def exit_scope(self):
        """Exit the current scope, but keep track of all declarations for error reporting."""
        # Before we pop, record all declarations from this scope in all_declarations
        for var in self.variable_scopes[-1]:
            self.all_declarations.add(var)

        # Now pop the scope
        self.variable_scopes.pop()
        self.scope_level -= 1

    def make_temporary_identifier(self, identifier: str) -> str:
        """Create a unique identifier for a variable in the current scope."""
        current_scope = self.variable_scopes[-1]

        # Check if variable already exists in current scope (shadowing is not allowed in same scope)
        if identifier in current_scope:
            raise Exception(f"Variable '{identifier}' already declared in this scope.")

        # Create unique name based on scope level and total occurrences
        # var_count = sum(1 for scope in self.variable_scopes if identifier in scope)
        unique_name = f"{identifier}.{self.scope_level}"  # .{var_count}"

        # Add to current scope
        current_scope[identifier] = unique_name
        self.original_variable_names.append(identifier)
        return unique_name

    def get_temporary_identifier(self, identifier: str) -> str:
        for scope in reversed(range(self.scope_level + 1)):
            if identifier in self.variable_scopes[scope]:
                return f"{identifier}.{scope}"  # self.variable_map[scope][identifier]

        raise Exception(f"Variable '{identifier}' not declared.")

    def parse(self, ast: ProgramNode) -> ProgramNode:

        if isinstance(ast, ProgramNode):
            for i, function in enumerate(ast.functions):
                if isinstance(function, FunctionNode):
                    ast.functions[0] = self.parse(function)

        elif isinstance(ast, FunctionNode):
            self.body = self.parse_block(ast.body)

        if self.label_calls:  # check if there are any label calls
            if not bool(set(self.label_declarations) & set(self.label_calls)):
                raise Exception(
                    f"Label name '{set(self.label_declarations) & set(self.label_calls)}' not declared."
                )

        return ast

    def parse_block(self, block: BlockNode) -> BlockNode:
        self.enter_scope()
        for i, block_item in enumerate(block.children):
            block.children[i] = self.parse_block_item(block_item)
        self.exit_scope()
        return block

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
        elif isinstance(content, BlockNode):
            block = self.parse_block(content)
            return BlockItemNode(block)
        else:
            raise Exception(f"Unknown block item type {content}.")

    def resolve_declaration(self, declaration: DeclarationNode) -> DeclarationNode:
        # Check if already declared in current scope
        if declaration.identifier in self.variable_scopes[-1]:
            raise Exception(f"Variable '{declaration.identifier}' already declared.")

        # Create unique name but DON'T add to current scope yet
        unique_name = f"{declaration.identifier}.{self.scope_level}"

        # Need to temporarily add the variable to the scope before resolving the expression
        # to handle cases where the variable is used in its own initialization
        self.variable_scopes[-1][declaration.identifier] = unique_name

        # Resolve the initialization expression (if any)
        resolved_exp = None
        if declaration.exp is not None:
            resolved_exp = self.resolve_expression(declaration.exp)

        # Variable is already added to current scope
        self.original_variable_names.append(declaration.identifier)

        return DeclarationNode(unique_name, resolved_exp)

    def resolve_statement(self, statement: Statement) -> Statement:

        if isinstance(statement, BlockNode):
            self.enter_scope()
            for i, block_item in enumerate(statement.children):
                statement.children[i] = self.parse_block_item(block_item)
            self.exit_scope()
            return statement

        elif isinstance(statement, ReturnNode):
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
            return VarNode(self.get_temporary_identifier(expression.identifier))
            # if expression.identifier in self.variable_map:
            #     return VarNode(self.get_temporary_identifier(expression.identifier))
            # else:
            #     raise Exception(f"Variable '{expression.identifier}' not declared.")
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
        print(ast)
        for function in ast.functions:
            print(function.body.__str__())
