from typing import Self
from enum import Enum


from .ParserConstructs import *


class Parser:
    def __init__(self, tokens: list[Token], debug) -> None:
        self.tokens = tokens
        self.ast = None
        self.debug = debug

    def parse(self) -> ProgramNode:
        program_node = ProgramNode()

        tokens = self.tokens
        while tokens:
            tokens, function = self.parse_function(tokens)
            program_node.functions.append(function)

        return program_node

    def parse_function(self, tokens: list[Token]) -> tuple[list[Token], FunctionNode]:

        tokens, _ = self.expect(Token("INT"), tokens)
        return_type = "INT"
        tokens, token = self.expect(Token("IDENTIFIER"), tokens)
        name = token.value

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        tokens, _ = self.expect(Token("VOID"), tokens)
        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)

        tokens, block_node = self.parse_block(tokens)

        return tokens, FunctionNode(return_type, name, block_node)

    def parse_block(self, tokens) -> tuple[list[Token], BlockNode]:
        block_items = []
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

        elif next_token == Token("SEMICOLON"):
            tokens = tokens[1:]
            return tokens, None
        else:
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, expression

    def parse_declaration(self, tokens) -> tuple[list[Token], DeclarationNode]:
        tokens, _ = self.expect(Token("INT"), tokens)
        tokens, identifier = self.expect(Token("IDENTIFIER"), tokens)
        identifier = identifier.value
        if tokens[0] == Token("EQUAL_ASSIGN"):
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            declaration = DeclarationNode(identifier, expression)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)
        else:
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)
            declaration = DeclarationNode(identifier, None)

        return tokens, declaration

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


def pretty_print(ast, level: int = 0, prev_content: str = "  ") -> None:
    print(ast)
    for function in ast.functions:
        print(function.body.__str__())
