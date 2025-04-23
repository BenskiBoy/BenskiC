from typing import Self
from enum import Enum


from .ParserConstructs import *


class Parser:
    def __init__(self, tokens: list[Token], debug) -> None:
        self.tokens = tokens
        self.ast = None
        self.debug = debug

    def parse(self) -> ProgramNode:

        tokens = self.tokens
        functions = []
        while tokens:
            tokens, function = self.parse_function(tokens)
            functions.append(function)
        program_node = ProgramNode(functions)

        return program_node

    def parse_function(
        self, tokens: list[Token]
    ) -> tuple[list[Token], FunctionDeclarationNode]:

        tokens, _ = self.expect(Token("INT"), tokens)
        return_type = "INT"
        tokens, token = self.expect(Token("IDENTIFIER"), tokens)
        name = token.value

        tokens, function_params = self.parse_function_parameter_list(tokens)
        for i, param in enumerate(function_params):
            function_params[i] = param

        tokens, block_node = self.parse_block(tokens)
        # if block_node.children == []:
        # block_node = BlockNode([])

        return tokens, FunctionDeclarationNode(name, function_params, block_node)

    def parse_function_parameter_list(
        self, tokens: list[Token]
    ) -> tuple[list[Token], list[str]]:
        parameters = []

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        if tokens[0] == Token("VOID"):
            tokens = tokens[1:]
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, parameters

        while tokens[0] != Token("CLOSE_PAREN"):
            if tokens[0] == Token("COMMA"):
                tokens = tokens[1:]

            tokens, _ = self.expect(Token("INT"), tokens)
            tokens, parameter = self.expect(Token("IDENTIFIER"), tokens)
            parameters.append(parameter.value)

        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
        return tokens, parameters

    def parse_argument_list(
        self, tokens: list[Token]
    ) -> tuple[list[Token], list[ExpressionNode]]:
        arguments = []

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        while tokens[0] != Token("CLOSE_PAREN"):

            if tokens[0] == Token("COMMA"):
                tokens = tokens[1:]

            tokens, expression = self.parse_expression(tokens)
            arguments.append(expression)

        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
        return tokens, arguments

    def parse_variable_declaration(
        self, tokens: list[Token]
    ) -> tuple[list[Token], VariableDeclarationNode]:
        tokens, _ = self.expect(Token("INT"), tokens)
        tokens, identifier = self.expect(Token("IDENTIFIER"), tokens)
        identifier = identifier.value

        if tokens[0] == Token("EQUAL_ASSIGN"):
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            declaration = VariableDeclarationNode(identifier, expression)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)
        else:
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)
            declaration = VariableDeclarationNode(identifier, None)

        return tokens, declaration

    def parse_block(self, tokens) -> tuple[list[Token], BlockNode]:
        block_items = []

        if tokens[0] == Token("SEMICOLON"):
            tokens = tokens[1:]
            return tokens, None

        tokens, _ = self.expect(Token("OPEN_BRACE"), tokens)

        while tokens[0].type != "CLOSE_BRACE":
            tokens, next_block_item = self.parse_block_item(tokens)
            block_items.append(next_block_item)

        tokens, _ = self.expect(Token("CLOSE_BRACE"), tokens)
        return tokens, BlockNode(block_items)

    def parse_block_item(self, tokens) -> tuple[list[Token], BlockItemNode]:
        if tokens[0] == Token("INT"):
            tokens, declaration = self.parse_declaration(tokens)
            block_item = BlockItemNode(declaration)
        else:
            tokens, statement = self.parse_statement(tokens)
            block_item = BlockItemNode(statement)
        return tokens, block_item

    def parse_statement(self, tokens) -> tuple[list[Token], Statement]:
        next_token = tokens[0]

        if next_token == Token("OPEN_BRACE"):
            tokens, block_node = self.parse_block(tokens)
            return tokens, block_node

        elif next_token == Token("RETURN"):
            tokens, _ = self.expect(Token("RETURN"), tokens)
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, ReturnNode(expression)

        elif next_token == Token("WHILE"):
            tokens, _ = self.expect(Token("WHILE"), tokens)
            tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)
            tokens, condition = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)

            tokens, body = self.parse_statement(tokens)

            return tokens, WhileNode(condition, body)

        elif next_token == Token("FOR"):
            tokens, _ = self.expect(Token("FOR"), tokens)
            tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

            # Parse the initialization statement
            if tokens[0] == Token("INT"):
                tokens, declaration = self.parse_variable_declaration(tokens)
                init_statement = InitDeclNode(declaration)
            else:
                if tokens[0] == Token("SEMICOLON"):
                    tokens = tokens[1:]
                    init_statement = None
                else:
                    tokens, init_statement = self.parse_expression(tokens)
                    init_statement = InitExprNode(init_statement)
                    tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            # Parse the condition expression
            if tokens[0] == Token("SEMICOLON"):
                tokens = tokens[1:]
                condition = None
            else:
                tokens, condition = self.parse_expression(tokens)
                tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            if tokens[0] == Token("CLOSE_PAREN"):
                post = None
            else:
                # Parse the body of the loop
                tokens, post = self.parse_expression(tokens)

            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)

            # Parse the body of the loop
            tokens, body = self.parse_statement(tokens)

            return tokens, ForNode(body, init_statement, condition, post)

        elif next_token == Token("BREAK"):
            tokens, _ = self.expect(Token("BREAK"), tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, BreakNode()

        elif next_token == Token("CONTINUE"):
            tokens, _ = self.expect(Token("CONTINUE"), tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, ContinueNode()

        elif next_token == Token("DO"):
            tokens, _ = self.expect(Token("DO"), tokens)
            # Special handling for empty statement case
            if tokens[0] == Token("SEMICOLON"):
                tokens = tokens[1:]  # Consume the semicolon
                body = None  # Empty statement
            else:
                tokens, body = self.parse_statement(tokens)

            tokens, _ = self.expect(Token("WHILE"), tokens)
            tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)
            tokens, condition = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, DoWhileNode(condition, body)

        elif next_token == Token("IF"):
            tokens, _ = self.expect(Token("IF"), tokens)
            tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)
            tokens, condition = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)

            tokens, then_block = self.parse_statement(tokens)

            if tokens[0] == Token("ELSE"):
                tokens = tokens[1:]
                if tokens[1] == Token("IF"):
                    tokens, _ = self.expect(Token("IF"), tokens)
                    tokens, condition = self.parse_expression(tokens)
                    tokens, then = self.parse_statement(tokens)
                    else_block = IfNode(condition, then)

                else:
                    tokens, else_block = self.parse_statement(tokens)
            else:
                else_block = None

            return tokens, IfNode(condition, then_block, else_block)

        elif next_token == Token("GOTO"):
            tokens, _ = self.expect(Token("GOTO"), tokens)
            tokens, label = self.expect(Token("IDENTIFIER"), tokens)
            label = label.value
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, GotoNode(label)
        elif next_token == Token("IDENTIFIER") and tokens[1] == Token("COLON"):
            label_name = next_token.value
            # label = LabelNode(label_name)
            tokens = tokens[2:]  # Skip the identifier and colon

            # Check if we're at a declaration (which would be invalid in C17)
            if tokens[0] == Token("INT"):
                raise Exception(
                    f"Syntax Error: Label '{label_name}' cannot be followed by a declaration in C17"
                )
            if tokens[0] == Token("CLOSE_BRACE"):
                raise Exception(
                    f"Syntax Error: Label '{label_name}' has nothing after it"
                )

            # If we're at an empty statement (semicolon), consume it and return the label
            if tokens[0] == Token("SEMICOLON"):
                tokens = tokens[1:]  # Skip the semicolon
                return tokens, LabeledStatementNode(label_name, None)

            # If we're at a regular statement, parse it
            tokens, statement = self.parse_statement(tokens)
            # If there's an empty statement after the label
            return tokens, LabeledStatementNode(label_name, statement)

        elif next_token == Token("SWITCH"):
            tokens, _ = self.expect(Token("SWITCH"), tokens)
            tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)
            tokens, condition = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)

            tokens, body = self.parse_statement(tokens)

            # Extract all case and default nodes from the body
            switch_body = []
            default = None

            if isinstance(body, DefaultNode):
                default = body
                switch_body.append(BlockItemNode(body))
            elif isinstance(body, CaseNode):
                switch_body.append(BlockItemNode(body))

            # If the body is a block node, we need to extract case and default statements
            elif isinstance(body, BlockNode):
                current_case = None

                for item in body.children:
                    content = item.child

                    if isinstance(content, CaseNode):
                        # Found a new case node
                        switch_body.append(BlockItemNode(content))
                        current_case = content

                    elif isinstance(content, DefaultNode) or default:
                        # Found the default node
                        if default is not None:  # and content is default:
                            raise Exception(
                                "Switch statement can't have multiple default clauses"
                            )
                        default = content  # used just to check if we've already added a default
                        current_case = None
                        switch_body.append(BlockItemNode(content))

                    elif current_case and content is not None:
                        # This statement belongs to the current case
                        # Append it to the current case's statement list
                        if current_case.body is None:
                            current_case.body = [content]
                        elif isinstance(content, list):
                            current_case.body.extend(BlockItemNode(content))
                        else:
                            current_case.body.append(BlockItemNode(content))
                    else:
                        # This is a statement outside any case/default - keep it
                        switch_body.append(item)

            return tokens, SwitchNode(condition, BlockNode(switch_body))

        elif next_token == Token("CASE"):
            tokens, _ = self.expect(Token("CASE"), tokens)
            tokens, expression = self.parse_expression(tokens)

            tokens, _ = self.expect(Token("COLON"), tokens)

            if tokens[0] in [Token("CASE"), Token("DEFAULT"), Token("CLOSE_BRACE")]:
                # Empty case body - no statements
                return tokens, CaseNode(
                    expression, [None]
                )  # Use [None] or [] to indicate empty body

            tokens, statement = self.parse_statement(tokens)

            return tokens, CaseNode(expression, [statement])

        elif next_token == Token("DEFAULT"):
            tokens, _ = self.expect(Token("DEFAULT"), tokens)
            tokens, _ = self.expect(Token("COLON"), tokens)
            tokens, statement = self.parse_statement(tokens)

            return tokens, DefaultNode([statement])

        elif next_token == Token("SEMICOLON"):
            tokens = tokens[1:]
            return tokens, None
        else:
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, expression

    def parse_declaration(self, tokens) -> tuple[list[Token], DeclarationNode]:
        if tokens[2] == Token("OPEN_PAREN"):
            # Function declaration
            tokens, function = self.parse_function(tokens)
            return tokens, function
        else:
            # Variable declaration
            tokens, variable_declaration = self.parse_variable_declaration(tokens)
            return tokens, variable_declaration

    def parse_conditional_middle(self, tokens) -> tuple[list[Token], ExpressionNode]:
        tokens, _ = self.expect(Token("QUESTION_MARK"), tokens)
        tokens, middle = self.parse_expression(tokens)
        tokens, _ = self.expect(Token("COLON"), tokens)
        return tokens, middle

    def parse_expression(
        self, tokens, min_prec: int = 0
    ) -> tuple[list[Token], ExpressionNode]:
        tokens, left = self.parse_factor(tokens)
        next_token = tokens[0]

        while (
            next_token in BINARY_TOKENS
            and TOKEN_PRECEDENCE[next_token.type] >= min_prec
        ):
            if next_token in [  # handle assignment operators
                Token(equal_node.name) for equal_node in EqualAssignOperatorNode
            ]:
                tokens = tokens[1:]  # consume the assignment operator
                tokens, right = self.parse_expression(
                    tokens, TOKEN_PRECEDENCE[next_token.type]
                )
                left = AssignmentNode(
                    left, right, EqualAssignOperatorNode[next_token.type]
                )

            elif next_token == Token("QUESTION_MARK"):
                tokens, middle = self.parse_conditional_middle(tokens)
                tokens, right = self.parse_expression(
                    tokens, TOKEN_PRECEDENCE[next_token.type]
                )
                left = ConditionalNode(left, middle, right)

            else:
                if isinstance(left, UnaryNode):
                    operator = self.parse_binary_operator(
                        next_token, left.operator == UnaryOperatorNode.NEGATE
                    )
                elif isinstance(left, BinaryNode):
                    operator = self.parse_binary_operator(next_token, False)
                elif isinstance(left, VarNode):
                    operator = self.parse_binary_operator(next_token, False)
                elif isinstance(left, ConstantNode):
                    operator = self.parse_binary_operator(next_token, False)
                elif isinstance(left, AssignmentNode):
                    operator = self.parse_binary_operator(next_token, False)
                elif isinstance(left, FunctionCallNode):
                    operator = self.parse_binary_operator(next_token, False)
                else:
                    raise Exception(f"Unexpected left operand type {type(left)}")
                tokens = tokens[1:]
                tokens, right = self.parse_expression(
                    tokens, TOKEN_PRECEDENCE[next_token.type] + 1
                )
                left = BinaryNode(operator, left, right)

            next_token = tokens[0]

        return tokens, left

    def parse_factor(
        self, tokens
    ) -> tuple[list[Token], UnaryNode | ExpressionNode | VarNode]:
        next_token = tokens[0]
        if next_token.type == "CONSTANT":
            return self.parse_constant(tokens)
        elif next_token in UNARY_TOKENS:
            tokens, operator = self.parse_unary(tokens)
            tokens, inner_expression = self.parse_factor(tokens)

            # Check for postfix operators after parsing the inner expression
            if tokens and tokens[0] in [Token("INCREMENT"), Token("DOUBLE_HYPHEN")]:
                next_token = tokens[0]
                tokens = tokens[1:]  # consume the token
                if next_token.type == "INCREMENT":
                    postfix_operator = UnaryOperatorNode.INCREMENT
                else:
                    postfix_operator = UnaryOperatorNode.DECREMENT
                inner_expression = UnaryNode(
                    inner_expression, postfix_operator, True
                )  # Apply postfix first

            return tokens, UnaryNode(inner_expression, operator)

        elif next_token.type == "OPEN_PAREN":
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, expression

        elif next_token.type == "IDENTIFIER":
            tokens, identifier = self.expect(Token("IDENTIFIER"), tokens)
            # Check for postfix operators immediately after identifier
            if tokens and tokens[0] in [Token("INCREMENT"), Token("DOUBLE_HYPHEN")]:
                next_token = tokens[0]
                tokens = tokens[1:]  # consume the token
                if next_token.type == "INCREMENT":
                    operator = UnaryOperatorNode.INCREMENT
                else:
                    operator = UnaryOperatorNode.DECREMENT
                return tokens, UnaryNode(VarNode(identifier.value), operator, True)

            elif tokens[0] == Token("OPEN_PAREN"):
                # Function call
                tokens, arguments = self.parse_argument_list(tokens)
                return tokens, FunctionCallNode(identifier.value, arguments)

            return tokens, VarNode(identifier.value)
        else:
            raise Exception(f"Syntax Error: Unexpected token {next_token}")

    def parse_unary(self, tokens) -> tuple[list[UnaryNode], str]:
        unary_operator = None
        if tokens[0].value == "~":
            unary_operator = UnaryOperatorNode.COMPLEMENT
        elif tokens[0].value == "-":
            unary_operator = UnaryOperatorNode.NEGATE
        elif tokens[0].value == "!":
            unary_operator = UnaryOperatorNode.NOT
        elif tokens[0].value == "++":
            unary_operator = UnaryOperatorNode.INCREMENT
        elif tokens[0].value == "--":
            unary_operator = UnaryOperatorNode.DECREMENT
        else:
            raise Exception(f"Unrecognised Unary Operator {tokens[0].value}")

        return tokens[1:], unary_operator

    def parse_binary_operator(
        self, token, negated_left_value
    ) -> (
        BinaryOperatorNode
    ):  # if the left value is negated, then the left shift is arithmetic
        if token == Token("ADD"):
            return BinaryOperatorNode.ADD
        elif token == Token("HYPHEN"):
            return BinaryOperatorNode.SUBTRACT
        elif token == Token("MULTIPLY"):
            return BinaryOperatorNode.MULTIPLY
        elif token == Token("DIVIDE"):
            return BinaryOperatorNode.DIVIDE
        elif token == Token("REMAINDER"):
            return BinaryOperatorNode.REMAINDER
        elif token == Token("AND_BITWISE"):
            return BinaryOperatorNode.AND_BITWISE
        elif token == Token("OR_BITWISE"):
            return BinaryOperatorNode.OR_BITWISE
        elif token == Token("XOR_BITWISE"):
            return BinaryOperatorNode.XOR_BITWISE
        elif token == Token("LEFT_SHIFT"):
            if negated_left_value:
                return BinaryOperatorNode.LEFT_SHIFT_ARITHMETIC
            else:
                return BinaryOperatorNode.LEFT_SHIFT_LOGICAL
        elif token == Token("RIGHT_SHIFT"):
            if negated_left_value:
                return BinaryOperatorNode.RIGHT_SHIFT_ARITHMETIC
            else:
                return BinaryOperatorNode.RIGHT_SHIFT_LOGICAL
        elif token == Token("AND_LOGICAL"):
            return BinaryOperatorNode.AND_LOGICAL
        elif token == Token("OR_LOGICAL"):
            return BinaryOperatorNode.OR_LOGICAL
        elif token == Token("EQUAL"):
            return BinaryOperatorNode.EQUAL
        elif token == Token("NOT_EQUAL"):
            return BinaryOperatorNode.NOT_EQUAL
        elif token == Token("LESS_OR_EQUAL"):
            return BinaryOperatorNode.LESS_OR_EQUAL
        elif token == Token("GREATER_OR_EQUAL"):
            return BinaryOperatorNode.GREATER_OR_EQUAL
        elif token == Token("LESS_THAN"):
            return BinaryOperatorNode.LESS_THAN
        elif token == Token("GREATER_THAN"):
            return BinaryOperatorNode.GREATER_THAN
        elif token == Token("LEFT_SHIFT_ASSIGN"):
            return BinaryOperatorNode.LEFT_SHIFT_ASSIGN
        elif token == Token("RIGHT_SHIFT_ASSIGN"):
            return BinaryOperatorNode.RIGHT_SHIFT_ASSIGN
        elif token == Token("ADD_ASSIGN"):
            return BinaryOperatorNode.ADD_ASSIGN
        elif token == Token("SUB_ASSIGN"):
            return BinaryOperatorNode.SUB_ASSIGN
        elif token == Token("MULT_ASSIGN"):
            return BinaryOperatorNode.MULT_ASSIGN
        elif token == Token("DIV_ASSIGN"):
            return BinaryOperatorNode.DIV_ASSIGN
        elif token == Token("AND_ASSIGN"):
            return BinaryOperatorNode.AND_ASSIGN
        elif token == Token("OR_ASSIGN"):
            return BinaryOperatorNode.OR_ASSIGN
        elif token == Token("XOR_ASSIGN"):
            return BinaryOperatorNode.XOR_ASSIGN
        elif token == Token("REM_ASSIGN"):
            return BinaryOperatorNode.REM_ASSIGN
        else:
            raise Exception(f"Unrecognised Binary Operator {token.value}")

    def parse_constant(self, tokens) -> tuple[list[Token], ConstantNode]:
        tokens, constant_token = self.expect(Token("CONSTANT"), tokens)

        return tokens, ConstantNode(constant_token.value)

    def expect(self, expected: Token, tokens: list[Token]) -> tuple[list[Token], Token]:
        if tokens[0].type == expected.type:
            return tokens[1:], tokens[0]
        raise Exception(f"Syntax Error: Expected {expected}, got {tokens[0]}")

    def pretty_print(self, ast, indent=0):
        """
        Pretty print the AST with proper indentation.

        Args:
            ast: The AST node to print
            indent: Current indentation level (default 0)
        """
        indent_str = "  " * indent

        if isinstance(ast, ProgramNode):
            print(f"{indent_str}Program:")
            for function in ast.functions:
                self.pretty_print(function, indent + 1)

        elif isinstance(ast, FunctionDeclarationNode):
            if ast.body:
                print(f"{indent_str}Function: {ast.identifier}")
                # print(f"{indent_str}Return Type: {ast.return_type}")
                # print(f"{indent_str}Parameters: {', '.join(str(ast.params)}")\
                for param in ast.params:
                    print(f"{indent_str}    Parameter: {param}")
                print(f"{indent_str}Body:")
                self.pretty_print(ast.body, indent + 1)
            else:
                print(f"{indent_str}Function Declaration: {ast.identifier}")
                # print(f"{indent_str}Return Type: {ast.return_type}")
                # print(f"{indent_str}    Parameters: {', '.join(ast.params)}")
                for param in ast.params:
                    print(f"{indent_str}    Parameter: {param}")

        elif isinstance(ast, BlockNode):
            print(f"{indent_str}Block:")
            for child in ast.children:
                self.pretty_print(child, indent + 1)

        elif isinstance(ast, BlockItemNode):
            self.pretty_print(ast.child, indent)

        elif isinstance(ast, DeclarationNode):
            init_str = ""
            if ast.exp:
                init_str = f" = {ast.exp}"
            print(f"{indent_str}Declaration: {ast.identifier}{init_str}")

        elif isinstance(ast, ReturnNode):
            print(f"{indent_str}Return:")
            self.pretty_print(ast.exp, indent + 1)

        elif isinstance(ast, IfNode):
            print(f"{indent_str}If:")
            print(f"{indent_str}  Condition:")
            self.pretty_print(ast.condition, indent + 2)
            print(f"{indent_str}  Then:")
            self.pretty_print(ast.then, indent + 2)
            if ast.else_:
                print(f"{indent_str}  Else:")
                self.pretty_print(ast.else_, indent + 2)

        elif isinstance(ast, WhileNode):
            print(f"{indent_str}While (label: {ast.label or 'None'}):")
            print(f"{indent_str}  Condition:")
            self.pretty_print(ast.condition, indent + 2)
            print(f"{indent_str}  Body:")
            self.pretty_print(ast.body, indent + 2)

        elif isinstance(ast, DoWhileNode):
            print(f"{indent_str}Do-While (label: {ast.label or 'None'}):")
            print(f"{indent_str}  Body:")
            self.pretty_print(ast.body, indent + 2)
            print(f"{indent_str}  Condition:")
            self.pretty_print(ast.condition, indent + 2)

        elif isinstance(ast, ForNode):
            print(f"{indent_str}For (label: {ast.label or 'None'}):")
            print(f"{indent_str}  Init:")
            if ast.init:
                self.pretty_print(ast.init, indent + 2)
            else:
                print(f"{indent_str}    None")
            print(f"{indent_str}  Condition:")
            if ast.condition:
                self.pretty_print(ast.condition, indent + 2)
            else:
                print(f"{indent_str}    None")
            print(f"{indent_str}  Update:")
            if ast.post:
                self.pretty_print(ast.post, indent + 2)
            else:
                print(f"{indent_str}    None")
            print(f"{indent_str}  Body:")
            self.pretty_print(ast.body, indent + 2)

        elif isinstance(ast, SwitchNode):
            print(f"{indent_str}Switch ({ast.label}):")
            if ast.case_targets:
                print(f"{indent_str}  Case Targets:")
                for case_target in ast.case_targets:
                    print(f"{indent_str}    {case_target}")
            if ast.default_target:
                print(f"{indent_str}  Default:")
                print(f"{indent_str}    {ast.default_target}")
            print(f"{indent_str}  Expression:")
            self.pretty_print(ast.condition, indent + 2)

            print(f"{indent_str}  Body:")
            self.pretty_print(ast.body, indent + 2)

        elif isinstance(ast, CaseNode):
            print(f"{indent_str}Case ({ast.label}):")
            print(f"{indent_str}  Condition:")
            self.pretty_print(ast.condition, indent + 2)
            print(f"{indent_str}  Statement:")
            if ast.body:
                self.pretty_print(ast.body, indent + 2)

            else:
                print(f"{indent_str}    None")

        elif isinstance(ast, DefaultNode):
            print(f"{indent_str}Default ({ast.label}):")
            if ast.body:
                self.pretty_print(ast.body, indent + 1)
            else:
                print(f"{indent_str}  None")

        elif isinstance(ast, BreakNode):
            print(
                f"{indent_str}Break (target: {ast.label if hasattr(ast, 'label') else 'None'})"
            )

        elif isinstance(ast, ContinueNode):
            print(
                f"{indent_str}Continue (target: {ast.label if hasattr(ast, 'label') else 'None'})"
            )

        elif isinstance(ast, GotoNode):
            print(f"{indent_str}Goto: {ast.label}")

        elif isinstance(ast, LabeledStatementNode):
            print(f"{indent_str}Label: {ast.label}")
            if ast.child:
                self.pretty_print(ast.child, indent + 1)

        elif isinstance(ast, VarNode):
            print(f"{indent_str}Variable: {ast.identifier}")

        elif isinstance(ast, ConstantNode):
            print(f"{indent_str}Constant: {ast.value}")

        elif isinstance(ast, BinaryNode):
            print(f"{indent_str}Binary Operation: {ast.operator}")
            print(f"{indent_str}  Left:")
            self.pretty_print(ast.exp_1, indent + 2)
            print(f"{indent_str}  Right:")
            self.pretty_print(ast.exp_2, indent + 2)

        elif isinstance(ast, UnaryNode):
            position = "Postfix" if ast.postfix else "Prefix"
            print(f"{indent_str}{position} Unary Operation: {ast.operator}")
            print(f"{indent_str}  Operand:")
            self.pretty_print(ast.exp, indent + 2)

        elif isinstance(ast, AssignmentNode):
            print(
                f"{indent_str}Assignment: {ast.type if hasattr(ast, 'type') else '='}"
            )
            print(f"{indent_str}  Left:")
            self.pretty_print(ast.lvalue, indent + 2)
            print(f"{indent_str}  Right:")
            self.pretty_print(ast.rvalue, indent + 2)

        elif isinstance(ast, ConditionalNode):
            print(f"{indent_str}Conditional (Ternary):")
            print(f"{indent_str}  Condition:")
            self.pretty_print(ast.condition, indent + 2)
            print(f"{indent_str}  Then:")
            self.pretty_print(ast.then, indent + 2)
            print(f"{indent_str}  Else:")
            self.pretty_print(ast.else_, indent + 2)

        elif isinstance(ast, list):
            print(f"{indent_str}List:")
            for item in ast:
                self.pretty_print(item, indent + 2)

        elif isinstance(ast, FunctionCallNode):
            print(f"{indent_str}Function Call: {ast.identifier}")
            print(f"{indent_str}  Arguments:")
            for arg in ast.arguments:
                self.pretty_print(arg, indent + 2)

        elif ast is None:
            print(f"{indent_str}None")

        else:
            print(f"{indent_str}Unknown Node Type: {type(ast).__name__}")
