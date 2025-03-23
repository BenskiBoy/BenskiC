from Tacky import *

from collections import defaultdict

###########################################


class Program:
    def __init__(self, program_name):
        self.globalls = []
        self.program_name = program_name

    def _gen_globals(self):
        res = ""
        for globall in self.globalls:
            res += f"   .global {globall}\n"
        return res

    def __str__(self):
        return f"""   {self._gen_globals()}"""


###########################################


class UnaryOperator:
    def __init__(self):
        pass


class UnaryOperatorNeg(UnaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"UnaryOperatorNeg"

    def __str__(self):
        return "negl"


class UnaryOperatorNot(UnaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"UnaryOperatorNot"

    def __str__(self):
        return "notl"


###########################################


class BinaryOperator:
    def __init__(self):
        pass


class BinaryOperatorAdd(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorAdd"

    def __str__(self):
        return "addl"


class BinaryOperatorSub(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorSub"

    def __str__(self):
        return "subl"


class BinaryOperatorMult(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorMult"

    def __str__(self):
        return "imull"


class BinaryOperatorAnd(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorAnd"

    def __str__(self):
        return "andl"


class BinaryOperatorOr(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorOr"

    def __str__(self):
        return "orl"


class BinaryOperatorXor(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorXor"

    def __str__(self):
        return "xorl"


class BinaryOperatorLeftShiftLogical(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorLeftShiftLogical"

    def __str__(self):
        return "shll"


class BinaryOperatorRightShiftLogical(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorRightShiftLogical"

    def __str__(self):
        return "shrl"


class BinaryOperatorLeftShiftArithmetic(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorLeftShiftArithmetic"

    def __str__(self):
        return "shll"


class BinaryOperatorRightShiftArithmetic(BinaryOperator):
    def __init__(self):
        pass

    def __repr__(self):
        return f"BinaryOperatorRightShiftArithmetic"

    def __str__(self):
        return "sarl"


###########################################


class Reg:
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"


class RegAX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%eax"


class RegR10(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%r10d"


class RegDX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%edx"


class RegCX(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%ecx"


class RegR11(Reg):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "%r11d"


###########################################


class Operand:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


class OperandImmediate(Operand):
    def __init__(self, value: int):
        super().__init__("Imm", value)

    def __str__(self):
        return f"${self.value}"


class OperandReg(Operand):
    def __init__(self, register: Reg):
        super().__init__("Reg", register)


class OperandPseudo(Operand):
    def __init__(self, indentifier: str):
        super().__init__("Pseudo", indentifier)


class OperandStack(Operand):
    def __init__(self, value: int):
        super().__init__("Stack", value)

    def __str__(self):
        return f"{self.value}(%rbp)"


###########################################


class Instruction:
    def __init__(self, command: str, arg_1=None, arg_2=None) -> None:
        self.command = command
        self.arg_1 = arg_1
        self.arg_2 = arg_2

    def __repr__(self) -> str:
        if not self.arg_1:
            return f"{self.__class__.__name__}"
        elif not self.arg_2:
            return f"{self.__class__.__name__} {repr(self.arg_1)}"
        else:
            return f"{self.__class__.__name__} {repr(self.arg_1)}, {repr(self.arg_2)}"

    def __str__(self) -> str:

        return f"   {self.command}   {str(self.arg_1)}{str(self.arg_2)}"


class InstructionMov(Instruction):
    def __init__(self, src: Operand, dst: Operand) -> None:
        super().__init__("movl", src, dst)

    def __str__(self):
        return f"   movl   {self.arg_1}, {self.arg_2}"


class InstructionBinary(Instruction):
    def __init__(
        self, binary_operator: BinaryOperator, src: Operand, dst: Operand
    ) -> None:
        super().__init__(binary_operator, src, dst)
        self.binary_operator = binary_operator

    def __str__(self):
        return f"   {str(self.binary_operator)}   {self.arg_1}, {self.arg_2}"

    def __repr__(self):
        return f"InstructionBinary {self.binary_operator.__class__.__name__}, {self.arg_1}, {self.arg_2}"


class InstructionIdiv(Instruction):
    def __init__(self, src: Operand) -> None:
        super().__init__("idivl", src)

    def __str__(self):
        return f"   idivl   {self.arg_1}"


class InstructionCdq(Instruction):
    def __init__(self):
        super().__init__("cdq")

    def __str__(self):
        return "   cdq"


class InstructionUnary(Instruction):
    def __init__(self, unary_operator: UnaryOperator, operand: Operand) -> None:
        super().__init__("Unary", unary_operator, operand)

    def __str__(self):
        return f"   {self.arg_1}   {self.arg_2}"


class InstructionAllocateStack(Instruction):
    def __init__(self, value) -> None:
        super().__init__("Unary", value)

    def __str__(self):
        return f"   subq   ${self.arg_1}, %rsp"


class InstructionRet(Instruction):
    def __init__(self) -> None:
        super().__init__("ret")

    # def __repr__(self):
    #     return f"InstructionRet[]"

    def __str__(self):
        return f"""   movq    %rbp, %rsp
   popq    %rbp
   ret"""


###########################################


class Function:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Func[{self.name}]"

    def __str__(self):
        return f"""
{self.name}:
   pushq   %rbp
   movq    %rsp, %rbp
"""


###########################################


class AssemblyParser:

    def __init__(self, program_name: str) -> None:
        self.program_name = program_name.replace("./", "")

        self.instructions = defaultdict(list)
        self.stack_tracker = defaultdict(dict)

    def generate_stack_pntr(self, pseudo_name: str, function_name: str = "") -> int:
        if function_name not in self.stack_tracker.keys():
            self.stack_tracker[function_name][pseudo_name] = (
                self.get_function_stack_size(function_name)
            )  # if function name doesn't exist, neitgher will pseudoname
            return self.stack_tracker[function_name][pseudo_name]
        else:
            if pseudo_name in self.stack_tracker[function_name].keys():
                return self.stack_tracker[function_name][pseudo_name]
            else:
                self.stack_tracker[function_name][pseudo_name] = (
                    self.get_function_stack_size(function_name) - 4
                )
            return self.stack_tracker[function_name][pseudo_name]

    def get_function_stack_size(self, function_name: str) -> int:
        max_size = -4
        for pseudo_name in self.stack_tracker[function_name].keys():
            if self.stack_tracker[function_name][pseudo_name] < max_size:
                max_size = self.stack_tracker[function_name][pseudo_name]
        return max_size

    def _parse_unary(self, op: str) -> UnaryOperator:
        if op == IRUnaryOperator.NEGATE:
            return UnaryOperatorNeg()
        elif op == IRUnaryOperator.COMPLEMENT:
            return UnaryOperatorNot()
        else:
            raise Exception(f"Unknown Unary Op {op}")

    def _parse_operand(self, node: IRNode):
        if isinstance(node, IRConstantNode):
            return OperandImmediate(node.value)
        elif isinstance(node, IRVarNode):
            return OperandPseudo(node.sources[0])

    def parse_unary(self, node: UnaryNode):
        return [
            InstructionMov(
                self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
            ),
            InstructionUnary(self._parse_unary(node.op), self._parse_operand(node.dst)),
        ]

    def parse_return(self, node: IRReturnNode):
        return [
            InstructionMov(self._parse_operand(node.sources[0]), RegAX()),
            InstructionRet(),
        ]

    def parse_constant(self, node: IRConstantNode):
        self.instructions.append(OperandImmediate(node.value))

    def parse_binary(self, node: IRBinaryNode):
        if node.op == BinaryOperatorNode.ADD:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorAdd(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.SUBTRACT:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorSub(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.MULTIPLY:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorMult(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.DIVIDE:
            return [
                InstructionMov(self._parse_operand(node.sources[0]), RegAX()),
                InstructionCdq(),
                InstructionIdiv(self._parse_operand(node.sources[1])),
                InstructionMov(RegAX(), self._parse_operand(node.dst)),
            ]
        elif node.op == BinaryOperatorNode.REMAINDER:
            return [
                InstructionMov(self._parse_operand(node.sources[0]), RegAX()),
                InstructionCdq(),
                InstructionIdiv(self._parse_operand(node.sources[1])),
                InstructionMov(RegDX(), self._parse_operand(node.dst)),
            ]
        elif node.op == BinaryOperatorNode.AND:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorAnd(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.OR:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorOr(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.XOR:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorXor(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.LEFT_SHIFT_LOGICAL:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorLeftShiftLogical(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.RIGHT_SHIFT_LOGICAL:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorRightShiftLogical(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.LEFT_SHIFT_ARITHMETIC:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorLeftShiftArithmetic(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == BinaryOperatorNode.RIGHT_SHIFT_ARITHMETIC:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), self._parse_operand(node.dst)
                ),
                InstructionBinary(
                    BinaryOperatorRightShiftArithmetic(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        else:
            raise Exception(f"Unknown Binary Op {node.op}")

    def parse(self, tacky: list[IRNode]):

        current_func_name = ""
        for i, tack in enumerate(tacky):
            if isinstance(tack, IRProgramNode):
                self.instructions["__PROGRAM__"].append(Program(self.program_name))

            elif isinstance(tack, IRFunctionNode):

                self.instructions[tack.name].append(Function(tack.name))
                current_func_name = tack.name
                self.instructions["__PROGRAM__"][0].globalls.append(tack.name)

            elif isinstance(tack, IRReturnNode):
                self.instructions[current_func_name].extend(self.parse_return(tack))

            elif isinstance(tack, IRUnaryNode):
                self.instructions[current_func_name].extend(self.parse_unary(tack))

            elif isinstance(tack, IRBinaryNode):
                self.instructions[current_func_name].extend(self.parse_binary(tack))

            else:
                raise Exception(f"Unknown IR {tack}")

        # Replace OperandPseudo with stack locations
        for j, func in enumerate(self.instructions.keys()):
            for i, inst in enumerate(self.instructions[func]):
                if (
                    isinstance(inst, InstructionMov)
                    or isinstance(inst, InstructionBinary)
                    or isinstance(inst, InstructionIdiv)
                ):
                    if isinstance(inst.arg_1, OperandPseudo):
                        self.instructions[func][i].arg_1 = OperandStack(
                            self.generate_stack_pntr(inst.arg_1.value, func)
                        )
                    if isinstance(inst.arg_2, OperandPseudo):
                        self.instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )
                elif isinstance(inst, InstructionUnary):
                    if isinstance(inst.arg_2, OperandPseudo):
                        self.instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )

            # add stack allocation
            if func in self.stack_tracker.keys():
                self.instructions[func].insert(
                    1, InstructionAllocateStack(self.get_function_stack_size(func) - 4)
                )

            for i, inst in enumerate(self.instructions[func]):
                if isinstance(
                    inst, InstructionMov
                ):  # (can't move stack values, need intermediary reg)
                    if isinstance(inst.arg_1, OperandStack) and isinstance(
                        inst.arg_2, OperandStack
                    ):

                        dest = inst.arg_2
                        self.instructions[func][i].arg_2 = RegR10()
                        self.instructions[func].insert(
                            i + 1, InstructionMov(RegR10(), dest)
                        )
                if isinstance(
                    inst, InstructionIdiv
                ):  # need to move immediate to R10D, then perform idiv on R10D
                    if isinstance(inst.arg_1, OperandImmediate):
                        val = inst.arg_1
                        self.instructions[func][i].arg_1 = RegR10()
                        self.instructions[func].insert(i, InstructionMov(val, RegR10()))

                if isinstance(inst, InstructionBinary):
                    if (
                        (
                            isinstance(inst.binary_operator, BinaryOperatorAdd)
                            or isinstance(inst.binary_operator, BinaryOperatorSub)
                        )
                        and isinstance(inst.arg_1, OperandStack)
                        and isinstance(inst.arg_2, OperandStack)
                    ):  # can't add or subtract stack values, need intermediary reg
                        dest = inst.arg_2
                        self.instructions[func][i].arg_2 = RegR10()
                        self.instructions[func].insert(
                            i, InstructionMov(dest, RegR10())
                        )
                        self.instructions[func][i + 1].arg_2 = RegR10()
                        self.instructions[func].insert(
                            i + 2, InstructionMov(RegR10(), dest)
                        )
                    if isinstance(inst.binary_operator, BinaryOperatorMult):
                        if isinstance(
                            inst.arg_2, OperandStack
                        ):  # can't use memory as operand for imull, need intermediary reg
                            dest = inst.arg_2
                            self.instructions[func].insert(
                                i, InstructionMov(dest, RegR11())
                            )
                            self.instructions[func][i + 1].arg_2 = RegR11()
                            self.instructions[func].insert(
                                i + 2, InstructionMov(RegR11(), dest)
                            )
                    if isinstance(
                        inst.binary_operator, BinaryOperatorLeftShiftLogical
                    ) or isinstance(
                        inst.binary_operator, BinaryOperatorRightShiftLogical
                    ):
                        if isinstance(inst.arg_2, OperandStack) and isinstance(
                            inst.arg_2, OperandStack
                        ):
                            src = inst.arg_1
                            dest = inst.arg_2
                            self.instructions[func].insert(
                                i,
                                InstructionMov(
                                    src, RegCX()
                                ),  # only cx can be used as shift count
                            )
                            self.instructions[func].insert(
                                i + 1, InstructionMov(dest, RegR10())
                            )
                            self.instructions[func][i + 2].arg_1 = RegCX()
                            self.instructions[func][i + 2].arg_2 = RegR10()
                            self.instructions[func].insert(
                                i + 3, InstructionMov(RegR10(), dest)
                            )
                    if (
                        isinstance(inst.binary_operator, BinaryOperatorAnd)
                        or isinstance(inst.binary_operator, BinaryOperatorOr)
                        or isinstance(inst.binary_operator, BinaryOperatorXor)
                    ):
                        if isinstance(inst.arg_1, OperandStack) and isinstance(
                            inst.arg_2, OperandStack
                        ):
                            src = inst.arg_1
                            dest = inst.arg_2
                            self.instructions[func].insert(
                                i, InstructionMov(src, RegCX())
                            )
                            self.instructions[func].insert(
                                i + 1, InstructionMov(dest, RegR10())
                            )
                            self.instructions[func][i + 2].arg_1 = RegCX()
                            self.instructions[func][i + 2].arg_2 = RegR10()
                            self.instructions[func].insert(
                                i + 3, InstructionMov(RegR10(), dest)
                            )

    def pretty_print(self):
        for func in self.instructions.keys():
            for inst in self.instructions[func]:
                print(repr(inst))

    def generate(self):
        res = ""
        for func in self.instructions.keys():
            for instr in self.instructions[func]:
                res += str(instr) + "\n"

        res += '   .section .note.GNU-stack,"",@progbits\n'

        return res
