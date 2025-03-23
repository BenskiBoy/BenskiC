from typing import Self
from enum import Enum


from .ParserConstructs import *


class Parser:
    def __init__(self, tokens: list[Token], debug) -> None:
        self.tokens = tokens
        self.ast = None
        self.debug = debug

    def parse(self) -> ASTNode:
        program_node = ProgramNode()

        tokens = self.tokens
        while tokens:
            tokens, function = self.parse_function(tokens)
            program_node.add_child(function)

        return program_node

    def parse_function(self, tokens: list[Token]) -> ASTNode:

        tokens, _ = self.expect(Token("INT"), tokens)
        return_type = "INT"
        tokens, token = self.expect(Token("IDENTIFIER"), tokens)
        name = token.value

        tokens, _ = self.expect(Token("OPEN_PAREN"), tokens)

        tokens, _ = self.expect(Token("VOID"), tokens)
        tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
        tokens, _ = self.expect(Token("OPEN_BRACE"), tokens)
        tokens, body = self.parse_statement(tokens)
        tokens, _ = self.expect(Token("CLOSE_BRACE"), tokens)
        return tokens, FunctionNode(return_type, name, [body])

    def parse_statement(self, tokens) -> ASTNode:
        tokens, _ = self.expect(Token("RETURN"), tokens)
        tokens, expression = self.parse_expression(tokens)
        tokens, _ = self.expect(Token("SEMICOLON"), tokens)

        return tokens, ReturnNode(expression)

    def parse_expression(self, tokens, min_prec: int = 0) -> ASTNode:
        tokens, left = self.parse_factor(tokens)
        next_token = tokens[0]

        while (
            next_token in BINARY_TOKENS
            and TOKEN_PRECEDENCE[next_token.type] >= min_prec
        ):
            operator = self.parse_binary_operator(
                next_token, left.operator == UnaryOperatorNode.NEGATE
            )
            tokens = tokens[1:]
            tokens, right = self.parse_expression(
                tokens, TOKEN_PRECEDENCE[next_token.type] + 1
            )
            left = BinaryNode(operator, left, right)

            next_token = tokens[0]

        return tokens, left

    def parse_factor(self, tokens) -> ASTNode:
        next_token = tokens[0]
        if next_token.type == "CONSTANT":
            return self.parse_constant(tokens)
        elif next_token.type == "TILDA" or next_token.type == "HYPHEN":
            tokens, operator = self.parse_unary(tokens)
            tokens, inner_expression = self.parse_factor(tokens)

            return tokens, UnaryNode(inner_expression, operator)

        elif next_token.type == "OPEN_PAREN":
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, expression
        else:
            raise Exception(f"Syntax Error: Unexpected token {next_token}")

    def parse_unary(self, tokens) -> tuple[list[ASTNode], str]:
        unary_operator = None
        if tokens[0].value == "~":
            unary_operator = UnaryOperatorNode.COMPLEMENT
        elif tokens[0].value == "-":
            unary_operator = UnaryOperatorNode.NEGATE
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
            return BinaryOperatorNode.AND
        elif token == Token("OR_BITWISE"):
            return BinaryOperatorNode.OR
        elif token == Token("XOR_BITWISE"):
            return BinaryOperatorNode.XOR
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
        else:
            raise Exception(f"Unrecognised Binary Operator {token.value}")

    def parse_constant(self, tokens) -> ASTNode:
        tokens, constant_token = self.expect(Token("CONSTANT"), tokens)

        return tokens, ConstantNode(constant_token.value)

    def expect(self, expected: Token, tokens: list[Token]) -> bool:
        if tokens[0].type == expected.type:
            return tokens[1:], tokens[0]
        raise Exception(f"Syntax Error: Expected {expected}, got {tokens[0]}")


def pretty_print(ast, level: int = 0, prev_content: str = "  ") -> None:
    print(" " * level + str(ast))
    print(" " * level + str(ast.children))
