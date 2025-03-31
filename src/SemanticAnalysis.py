from parser.ParserConstructs import *
from collections import defaultdict


class SemanticAnalysis:
    def __init__(self):
        self.variable_map = defaultdict(int)

    def make_temporary_identifier(self, identifier: str) -> str:
        if identifier not in self.variable_map:
            self.variable_map[identifier] = 0
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

    def parse(self, ast: ASTNode) -> ASTNode:

        if isinstance(ast, ProgramNode):
            for i, child in enumerate(ast.children):
                if isinstance(child, FunctionNode):
                    ast.children[0] = self.parse(child)

        elif isinstance(ast, FunctionNode):
            for i, child in enumerate(ast.children):
                for j, block_item in enumerate(child):
                    res = self.parse_block_item(block_item)
                    ast.children[i][j] = res

        return ast

    def parse_block_item(self, block: BlockItemNode) -> BlockItemNode:

        content = block.children[0]
        if isinstance(content, DeclarationNode):
            return BlockItemNode(self.resolve_declaration(content))
        elif isinstance(content, ReturnNode) or isinstance(
            block, ExpressionNode
        ):  # statement
            return BlockItemNode(self.resolve_statement(content))
        elif isinstance(content, ExpressionNode):
            return BlockItemNode(self.resolve_expression(content))
        elif content is None:
            return BlockItemNode(None)
        else:
            raise Exception(f"Unknown block item type {content.type}.")

    def resolve_declaration(self, declaration: DeclarationNode) -> DeclarationNode:
        if declaration.identifier in self.variable_map:
            raise Exception(f"Variable '{declaration.identifier}' already declared.")

        unique_name = self.make_temporary_identifier(declaration.identifier)
        if declaration.children[0] is not None:
            expression = self.resolve_expression(declaration.children[0])
        else:
            expression = None

        return DeclarationNode(
            unique_name,
            expression,
        )

    def resolve_statement(self, statement: Statement) -> Statement:
        if isinstance(statement.children[0], ReturnNode):
            return ReturnNode(self.resolve_expression(statement.children))
        elif isinstance(statement.children[0], ExpressionNode):
            expression = self.resolve_expression(statement.children[0])
            return ExpressionNode("EXPRESSION", expression)
        else:
            raise Exception("Unknown statement type.")

    def resolve_expression(self, expression: ExpressionNode) -> ExpressionNode:

        print(f"resolving expression? {repr(expression)}")
        if len(expression.children) == 0:
            if isinstance(expression, VarNode):
                if expression.identifier in self.variable_map:
                    return VarNode(self.get_temporary_identifier(expression.identifier))
                else:
                    raise Exception(f"Variable '{expression.identifier}' not declared.")
            else:
                return expression
        elif isinstance(
            expression.children[0],
            AssignmentNode,
        ):
            if not isinstance(expression.children[0].children[0], VarNode):
                raise Exception("Left side of assignment must be a variable.")
            if isinstance(expression.children[0].children[1], AssignmentNode):
                raise Exception("Assignment cannot be nested.")  # i.e. a = b = c
            return AssignmentNode(
                self.resolve_expression(expression.children[0].children[0]),
                self.resolve_expression(expression.children[0].children[1]),
            )
        elif isinstance(expression, BinaryNode):
            left = self.resolve_expression(expression.children[0])
            right = self.resolve_expression(expression.children[1])
            return BinaryNode(
                expression.operator,
                left,
                right,
            )
        elif isinstance(expression, UnaryNode):
            child = self.resolve_expression(expression.children[0])
            return UnaryNode(child, expression.operator)

        else:
            return expression

    def pretty_print(self, ast):
        print(self.variable_map)
        print(repr(ast))
