from enum import Enum


class IRUnaryOperator(Enum):
    COMPLEMENT = "Complement"
    NEGATE = "Negate"


class IRBinaryOperator(Enum):
    ADD = "Add"
    SUBTRACT = "Subtract"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"
    REMAINDER = "Remainder"


class IRNode:
    def __init__(self, op: str, sources: [["IRNode"]], dst: ["IRNode"]) -> None:
        self.op = op
        self.sources = sources
        self.dst = dst

    def __str__(self) -> str:
        return f"""IRNode({self.op}, {self.sources}, {self.dst})"""


class IRConstantNode(IRNode):
    def __init__(self, value: str) -> None:
        super().__init__("CONSTANT", None, None)
        self.value = value

    def __str__(self) -> str:
        return f"""IRConstantNode({self.value})"""

    def __repr__(self) -> str:
        return f"""IRConstantNode({self.value})"""


class IRUnaryNode(IRNode):
    def __init__(self, op: IRUnaryOperator, src: IRNode, dst: IRNode) -> None:
        super().__init__(op, [src], dst)

    def __str__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.sources[0]}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRUnaryNode({self.op}, {self.sources[0]}, {self.dst})"""


class IRBinaryNode(IRNode):
    def __init__(
        self, op: IRBinaryOperator, src_1: IRNode, src_2: IRNode, dst: IRNode
    ) -> None:
        super().__init__(op, [src_1, src_2], dst)

    def __str__(self) -> str:
        return f"""IRBinaryNode({self.op}, {self.sources[0]}, {self.sources[1]}, {self.dst})"""

    def __repr__(self) -> str:
        return f"""IRBinaryNode({self.op}, {self.sources[0]}, {self.sources[1]}, {self.dst})"""


class IRVarNode(IRNode):
    def __init__(self, name: str) -> None:
        super().__init__("VAR", [name], [])

    def __str__(self) -> str:
        return f"""IRVarNode({self.sources[0]})"""

    def __repr__(self) -> str:
        return f"""IRVarNode({self.sources[0]})"""


class IRProgramNode(IRNode):
    def __init__(
        self,
    ) -> None:
        super().__init__("PROGRAM", None, [])

    def __str__(self) -> str:
        return f"""IRProgramNode()"""

    def __repr__(self) -> str:
        return f"""IRProgramNode()"""


class IRFunctionNode(IRNode):
    def __init__(self, name: str, return_type) -> None:
        super().__init__("Function", None, [])
        self.name = name
        self.return_type = return_type

    def __str__(self) -> str:
        return f"""IRFunctionNode({self.name}, {self.return_type})"""

    def __repr__(self) -> str:
        return f"""IRFunctionNode({self.name}, {self.return_type})"""


class IRReturnNode(IRNode):
    def __init__(self, val: IRNode) -> None:
        super().__init__("RETURN", [val], None)

    def __str__(self) -> str:
        return f"""IRReturnNode({self.sources[0]})"""

    def __repr__(self) -> str:
        return f"""IRReturnNode({self.sources[0]})"""
