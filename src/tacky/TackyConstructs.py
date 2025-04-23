from enum import Enum
from typing import Self
from parser.Parser import *


class IRNode:
    def __init__(self, op: str, sources: list[Self], dst: Self) -> None:
        self.op = op
        self.sources = sources
        self.dst = dst

    def __str__(self) -> str:
        return f"""IRNode({self.op}, {self.sources}, {self.dst})"""


# Val
class IRConstantNode(IRNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", None, None)
        self.value = value

    def __str__(self) -> str:
        return f"""IRConstantNode({self.value})"""

    def __repr__(self) -> str:
        return f"""IRConstantNode({self.value})"""


class IRVarNode(IRNode):
    def __init__(self, name: str) -> None:
        super().__init__("VAR", [name], [])

    def __str__(self) -> str:
        return f"""IRVarNode({self.sources[0]})"""

    def __repr__(self) -> str:
        return f"""IRVarNode({self.sources[0]})"""


### Instructions
class IRReturnNode(IRNode):
    def __init__(self, val: IRConstantNode | IRVarNode) -> None:
        super().__init__("RETURN", [val], None)

    def __str__(self) -> str:
        return f"""IRReturnNode({self.sources[0]})"""

    def __repr__(self) -> str:
        return f"""IRReturnNode({self.sources[0]})"""


class IRCopyNode(IRNode):
    def __init__(
        self, src: IRConstantNode | IRVarNode, dst: IRConstantNode | IRVarNode
    ) -> None:
        super().__init__("COPY", [src], dst)

    def __str__(self) -> str:
        return f"""IRCopyNode({self.sources[0]} to {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRCopyNode({self.sources[0]} to {self.dst})"""


class IRJumpNode(IRNode):
    def __init__(self, target: str) -> None:
        super().__init__("JUMP", [], None)
        self.target = target

    def __str__(self) -> str:
        return f"""IRJumpNode({self.target})"""

    def __repr__(self) -> str:
        return f"""IRJumpNode({self.target})"""


class IRJumpIfZeroNode(IRNode):
    def __init__(self, condition: IRConstantNode | IRVarNode, target: str) -> None:
        super().__init__("JUMP_IF_ZERO", [], None)
        self.target = target
        self.condition = condition

    def __str__(self) -> str:
        return f"""IRJumpIfZeroNode({self.target}, {self.condition})"""

    def __repr__(self) -> str:
        return f"""IRJumpIfZeroNode({self.target}, {self.condition})"""


class IRJumpIfNotZeroNode(IRNode):
    def __init__(self, condition: IRConstantNode | IRVarNode, target: str) -> None:
        super().__init__("JUMP_IF_NOT_ZERO", [], None)
        self.target = target
        self.condition = condition

    def __str__(self) -> str:
        return f"""IRJumpIfNotZeroNode({self.target}, {self.condition})"""

    def __repr__(self) -> str:
        return f"""IRJumpIfNotZeroNode({self.target}, {self.condition})"""


class IRLabelNode(IRNode):
    def __init__(self, identifier) -> None:
        super().__init__("LABEL", [], None)
        self.identifier = identifier

    def __str__(self) -> str:
        return f"""IRLabelNode({self.identifier})"""

    def __repr__(self) -> str:
        return f"""IRLabelNode({self.identifier})"""


class IRFunctionCallNode(IRNode):
    def __init__(
        self,
        identifier: str,
        args: list[IRConstantNode | IRVarNode],
        dst: IRConstantNode | IRVarNode,
    ) -> None:
        super().__init__("FunctionCall", args, dst)
        self.identifier = identifier
        self.dst = dst

    def __str__(self) -> str:
        return f"""FunctionCallNode({self.identifier}, {self.sources}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""FunctionCallNode({self.identifier}, {self.sources}, {self.dst})"""


##### Unary
class IRUnaryOperator(Enum):
    COMPLEMENT = "Complement"
    NEGATE = "Negate"
    NOT = "Not"
    INCREMENT = "Increment"
    DECREMENT = "Decrement"


class IRUnaryNode(IRNode):
    def __init__(
        self,
        op: IRUnaryOperator,
        src: IRConstantNode | IRVarNode,
        dst: IRConstantNode | IRVarNode,
    ) -> None:
        super().__init__(op, [src], dst)

    def __str__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.sources[0]}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.sources[0]}, {self.dst})"""


##### Binary
class IRBinaryOperator(Enum):
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"
    REMAINDER = "Remainder"
    AND_BITWISE = "AndBitwise"
    OR_BITWISE = "OrBitwise"
    XOR_BITWISE = "XorBitwise"
    LEFT_SHIFT_LOGICAL = "LeftShiftLogical"
    RIGHT_SHIFT_LOGICAL = "RightShiftLogical"
    LEFT_SHIFT_ARITHMETIC = "LeftShiftArithmetic"
    RIGHT_SHIFT_ARITHMETIC = "RightShiftArithmetic"
    AND_LOGICAL = "AndLogical"
    OR_LOGICAL = "OrLogical"
    EQUAL = "Equal"
    NOT_EQUAL = "NotEqual"
    LESS_THAN = "LessThan"
    GREATER_THAN = "GreaterThan"
    LESS_OR_EQUAL = "LessOrEqual"
    GREATER_OR_EQUAL = "GreaterOrEqual"


IR_BINARY_RELATIONAL_OPERATORS = [
    IRBinaryOperator.EQUAL,
    IRBinaryOperator.NOT_EQUAL,
    IRBinaryOperator.LESS_THAN,
    IRBinaryOperator.GREATER_THAN,
    IRBinaryOperator.LESS_OR_EQUAL,
    IRBinaryOperator.GREATER_OR_EQUAL,
]

IR_BINARY_NON_SHORT_CIRCUIT_OPERATORS = [
    IRBinaryOperator.ADD,
    IRBinaryOperator.SUBTRACT,
    IRBinaryOperator.MULTIPLY,
    IRBinaryOperator.DIVIDE,
    IRBinaryOperator.REMAINDER,
    IRBinaryOperator.AND_BITWISE,
    IRBinaryOperator.OR_BITWISE,
    IRBinaryOperator.XOR_BITWISE,
    IRBinaryOperator.LEFT_SHIFT_LOGICAL,
    IRBinaryOperator.RIGHT_SHIFT_LOGICAL,
    IRBinaryOperator.LEFT_SHIFT_ARITHMETIC,
    IRBinaryOperator.RIGHT_SHIFT_ARITHMETIC,
    IRBinaryOperator.EQUAL,
    IRBinaryOperator.NOT_EQUAL,
    IRBinaryOperator.LESS_THAN,
    IRBinaryOperator.GREATER_THAN,
    IRBinaryOperator.LESS_OR_EQUAL,
    IRBinaryOperator.GREATER_OR_EQUAL,
]
IR_BINARY_SHORT_CIRCUIT_OPERATORS = [
    IRBinaryOperator.AND_LOGICAL,
    IRBinaryOperator.OR_LOGICAL,
]

ASSIGN_EQUAL_OPERATORS_LOOKUP = {
    EqualAssignOperatorNode.ADD_ASSIGN: IRBinaryOperator.ADD,
    EqualAssignOperatorNode.SUB_ASSIGN: IRBinaryOperator.SUBTRACT,
    EqualAssignOperatorNode.MULT_ASSIGN: IRBinaryOperator.MULTIPLY,
    EqualAssignOperatorNode.DIV_ASSIGN: IRBinaryOperator.DIVIDE,
    EqualAssignOperatorNode.REM_ASSIGN: IRBinaryOperator.REMAINDER,
    EqualAssignOperatorNode.AND_ASSIGN: IRBinaryOperator.AND_BITWISE,
    EqualAssignOperatorNode.OR_ASSIGN: IRBinaryOperator.OR_BITWISE,
    EqualAssignOperatorNode.XOR_ASSIGN: IRBinaryOperator.XOR_BITWISE,
    EqualAssignOperatorNode.LEFT_SHIFT_ASSIGN: IRBinaryOperator.LEFT_SHIFT_LOGICAL,
    EqualAssignOperatorNode.RIGHT_SHIFT_ASSIGN: IRBinaryOperator.RIGHT_SHIFT_LOGICAL,
}


class IRBinaryNode(IRNode):
    def __init__(
        self,
        op: IRBinaryOperator,
        src_1: IRConstantNode | IRVarNode,
        src_2: IRConstantNode | IRVarNode,
        dst: IRConstantNode | IRVarNode,
    ) -> None:
        super().__init__(op, [src_1, src_2], dst)

    def __str__(self) -> str:
        return f"""IRBinaryNode({self.op}, {self.sources[0]}, {self.sources[1]}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRBinaryNode({self.op}, {self.sources[0]}, {self.sources[1]}, {self.dst})"""


class IRFunctionNode(IRNode):
    def __init__(self, identifier: str, params: list[str], body: list[IRNode]) -> None:
        super().__init__("Function", [], None)
        self.identifier = identifier
        self.params = params
        self.body = body

    def __str__(self) -> str:
        return f"""IRFunctionNode({self.identifier}, {self.params})"""

    def __repr__(self) -> str:
        return f"""IRFunctionNode({self.identifier}, {self.params})"""


class IRProgramNode(IRNode):
    def __init__(
        self,
        function_definitions: list[IRFunctionNode],
    ) -> None:
        super().__init__("PROGRAM", None, [])
        self.function_definitions = function_definitions

    def __str__(self) -> str:
        return f"""IRProgramNode({self.function_definitions})"""

    def __repr__(self) -> str:
        return f"""IRProgramNode({self.function_definitions})"""
