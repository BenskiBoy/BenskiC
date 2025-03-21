from typing import Self

from Lexer import Token


class ASTNode:
    def __init__(self, type: str, children: list[Self] = []) -> None:
        self.type = type
        self.children = children

    def add_child(self, child: Self) -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        return f"{self.type}({self.children})"


class ReturnNode(ASTNode):
    def __init__(self, child: ASTNode) -> None:
        super().__init__("RETURN", [child])

    def __str__(self) -> str:
        return f"""Return("""


class ConstantNode(ASTNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", [])
        self.value = value

    def __str__(self) -> str:
        return f"""Constant({self.value})"""

    def __repr__(self) -> str:
        return f"""CONSTANT({self.value})"""


class UnaryNode(ASTNode):
    def __init__(self, operator: str, child: ASTNode) -> None:
        super().__init__("UNARY", [child])
        self.operator = operator

    def __str__(self) -> str:
        return f"""Unary({self.operator}, {self.children[0]})"""


class FunctionNode(ASTNode):
    def __init__(self, return_type: str, name: str, body: list[ASTNode]) -> None:
        super().__init__("FUNCTION", body)
        self.return_type = return_type
        self.name = name

    def assemble(self) -> str:
        return f"""
        .global {self.name}
        {self.name}:
        """

    def __str__(self) -> str:
        return f"""
Function(
    name = {self.name}
    return_type = {self.return_type}
    body = """


class ProgramNode(ASTNode):
    def __init__(self) -> None:
        super().__init__("PROGRAM", [])

    def __str__(self) -> str:
        return f"""
Program("""


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

    def parse_expression(self, tokens) -> ASTNode:
        next_token = tokens[0]
        if next_token.type == "CONSTANT":
            return self.parse_constant(tokens)
        elif next_token.type == "TILDA" or next_token.type == "HYPHEN":
            tokens, operator = self.parse_unary(tokens)
            tokens, inner_expression = self.parse_expression(tokens)

            return tokens, UnaryNode(operator, inner_expression)

        elif next_token.type == "OPEN_PAREN":
            tokens = tokens[1:]
            tokens, expression = self.parse_expression(tokens)
            tokens, _ = self.expect(Token("CLOSE_PAREN"), tokens)
            return tokens, expression
        else:
            raise Exception(f"Syntax Error: Unexpected token {next_token}")
        # tokens, constnat = self.parse_constant(tokens)
        # return tokens, constnat

    def parse_unary(self, tokens) -> tuple[list[ASTNode], str]:
        return tokens[1:], tokens[0].value

    def parse_constant(self, tokens) -> ASTNode:
        tokens, constant_token = self.expect(Token("CONSTANT"), tokens)

        return tokens, ConstantNode(constant_token.value)

    def expect(self, expected: Token, tokens: list[Token]) -> bool:
        if tokens[0].type == expected.type:
            return tokens[1:], tokens[0]
        raise Exception(f"Syntax Error: Expected {expected}, got {tokens[0]}")


def pretty_print(ast, level: int = 0, prev_content: str = "  ") -> None:
    # go through each node and print it out, recursively, with proper indentation

    if level == 0:
        print(ast)
        for child in ast.children:
            pretty_print(child, level + 1)
        print(")")

    elif len(ast.children) == 0:
        print(" " * level + str(ast))
    elif len(ast.children) == 1:
        content = str(ast)

        end_char = "\n"
        if content[-2] == "=":
            end_char = ""

        indent = level
        if prev_content[-2] == "=":
            indent = 0

        print("\t" * indent + content, end=end_char)
        pretty_print(ast.children[0], level + 1, prev_content=content)
        print(")")
