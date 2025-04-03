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

        block_items = []

        tokens, _ = self.expect(Token("INT"), tokens)
        return_type = "INT"
        tokens, token = self.expect(Token("IDENTIFIER"), tokens)
        name = token.value

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        tokens, _ = self.expect(Token("VOID"), tokens)
        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
        tokens, _ = self.expect(Token("OPEN_BRACE"), tokens)

        while tokens[0].type != "CLOSE_BRACE":
            tokens, next_block_item = self.parse_block_item(tokens)
            block_items.append(next_block_item)

        tokens, _ = self.expect(Token("CLOSE_BRACE"), tokens)
        return tokens, FunctionNode(return_type, name, [block_items])

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
        if next_token == Token("RETURN"):
            tokens, _ = self.expect(Token("RETURN"), tokens)
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("SEMICOLON"), tokens)

            return tokens, ReturnNode(expression)
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

    def parse_expression(
        self, tokens, min_prec: int = 0
    ) -> tuple[list[Token], ExpressionNode]:
        tokens, left = self.parse_factor(tokens)
        next_token = tokens[0]

        while (
            next_token in BINARY_TOKENS
            and TOKEN_PRECEDENCE[next_token.type] >= min_prec
        ):
            if next_token == Token("EQUAL_ASSIGN"):

                tokens = tokens[1:]  # consume the assignment operator
                tokens, right = self.parse_expression(
                    tokens, TOKEN_PRECEDENCE[next_token.type]
                )
                left = AssignmentNode(left, right)
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
        elif (
            next_token.type == "TILDA"
            or next_token.type == "HYPHEN"
            or next_token.type == "NOT"
        ):
            tokens, operator = self.parse_unary(tokens)
            tokens, inner_expression = self.parse_factor(tokens)

            return tokens, UnaryNode(inner_expression, operator)

        elif next_token.type == "OPEN_PAREN":
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, expression

        elif next_token.type == "IDENTIFIER":
            tokens, identifier = self.expect(Token("IDENTIFIER"), tokens)
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
        print(function.__str__())
        for block in function.block_items:
            for item in block:
                print(repr(item))
