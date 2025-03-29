from tacky.TackyConstructs import *
from .AssemblerConstructs import *
from collections import defaultdict

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

    def _parse_unary_type(self, op: str) -> UnaryOperator:
        if op == IRUnaryOperator.NEGATE:
            return UnaryOperatorNeg()
        elif op == IRUnaryOperator.COMPLEMENT:
            return UnaryOperatorNot()
        elif op == IRUnaryOperator.NOT:
            return UnaryOperatorNot()
        else:
            raise Exception(f"Unknown Unary Op {op}")

    def _parse_operand(self, node: IRNode):
        if isinstance(node, IRConstantNode):
            return OperandImmediate(node.value)
        elif isinstance(node, IRVarNode):
            return OperandPseudo(node.sources[0])

    def _parse_relational_type(self, op: IRBinaryOperator) -> ConditionCode:
        if op == IRBinaryOperator.GREATER_THAN:
            return ConditionCodeGreater()
        elif op == IRBinaryOperator.GREATER_OR_EQUAL:
            return ConditionCodeGreaterOrEqual()
        elif op == IRBinaryOperator.LESS_THAN:
            return ConditionCodeLess()
        elif op == IRBinaryOperator.LESS_OR_EQUAL:
            return ConditionCodeLessOrEqual()
        elif op == IRBinaryOperator.EQUAL:
            return ConditionCodeEqual()
        elif op == IRBinaryOperator.NOT_EQUAL:
            return ConditionCodeNotEqual()
        else:
            raise Exception(f"Unknown Relational Op {op}")

    def parse_unary(self, node: IRUnaryNode):
        if node.op == IRUnaryOperator.NOT:
            return [
                InstructionCmp(
                    OperandImmediate(0),
                    self._parse_operand(node.sources[0]),
                    "Performing NOT",
                ),
                InstructionMov(OperandImmediate(0), self._parse_operand(node.dst)),
                InstructionSetCC(ConditionCodeEqual(), self._parse_operand(node.dst)),
            ]
        elif node.op in [IRUnaryOperator.COMPLEMENT, IRUnaryOperator.NEGATE]:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    f"Performing {node.op}",
                ),
                InstructionUnary(
                    self._parse_unary_type(node.op), self._parse_operand(node.dst)
                ),
            ]
        else:
            raise Exception(f"Unknown Unary Op {node.op}")

    def parse_return(self, node: IRReturnNode):
        return [
            InstructionMov(self._parse_operand(node.sources[0]), RegAX()),
            InstructionRet(),
        ]

    def parse_constant(self, node: IRConstantNode):
        self.instructions.append(OperandImmediate(node.value))

    def parse_binary(self, node: IRBinaryOperator):
        if node.op == IRBinaryOperator.ADD:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing ADD",
                ),
                InstructionBinary(
                    BinaryOperatorAdd(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.SUBTRACT:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing SUBTRACT",
                ),
                InstructionBinary(
                    BinaryOperatorSub(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.MULTIPLY:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing MULTIPLY",
                ),
                InstructionBinary(
                    BinaryOperatorMult(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.DIVIDE:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]), RegAX(), "Performing DIVIDE"
                ),
                InstructionCdq(),
                InstructionIdiv(self._parse_operand(node.sources[1])),
                InstructionMov(RegAX(), self._parse_operand(node.dst)),
            ]
        elif node.op == IRBinaryOperator.REMAINDER:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    RegAX(),
                    "Performing REMAINDER",
                ),
                InstructionCdq(),
                InstructionIdiv(self._parse_operand(node.sources[1])),
                InstructionMov(RegDX(), self._parse_operand(node.dst)),
            ]
        elif node.op == IRBinaryOperator.AND_BITWISE:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing AND_BITWISE",
                ),
                InstructionBinary(
                    BinaryOperatorAnd(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.OR_BITWISE:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing OR_BITWISE",
                ),
                InstructionBinary(
                    BinaryOperatorOr(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.XOR_BITWISE:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing XOR_BITWISE",
                ),
                InstructionBinary(
                    BinaryOperatorXor(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.LEFT_SHIFT_LOGICAL:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing LEFT_SHIFT_LOGICAL",
                ),
                InstructionBinary(
                    BinaryOperatorLeftShiftLogical(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.RIGHT_SHIFT_LOGICAL:
            return [
                InstructionMov(
                    self._parse_operand(node.sources[0]),
                    self._parse_operand(node.dst),
                    "Performing RIGHT_SHIFT_LOGICAL",
                ),
                InstructionBinary(
                    BinaryOperatorRightShiftLogical(),
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.dst),
                ),
            ]
        elif node.op == IRBinaryOperator.LEFT_SHIFT_ARITHMETIC:
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
        elif node.op == IRBinaryOperator.RIGHT_SHIFT_ARITHMETIC:
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

        elif node.op in IR_BINARY_RELATIONAL_OPERATORS:
            return [
                InstructionCmp(
                    self._parse_operand(node.sources[1]),
                    self._parse_operand(node.sources[0]),
                ),
                InstructionMov(OperandImmediate(0), self._parse_operand(node.dst)),
                InstructionSetCC(
                    self._parse_relational_type(node.op), self._parse_operand(node.dst)
                ),
            ]

        else:
            raise Exception(f"Unknown Binary Op {node.op}")

    def place_stack(
        self, instructions: dict[str, list[Instruction]]
    ) -> dict[str, list[Instruction]]:
        for j, func in enumerate(instructions.keys()):
            for i, inst in enumerate(instructions[func]):
                if (
                    isinstance(inst, InstructionMov)
                    or isinstance(inst, InstructionBinary)
                    or isinstance(inst, InstructionIdiv)
                    or isinstance(inst, InstructionCmp)
                    or isinstance(inst, InstructionSetCC)
                ):
                    if isinstance(inst.arg_1, OperandPseudo):
                        instructions[func][i].arg_1 = OperandStack(
                            self.generate_stack_pntr(inst.arg_1.value, func)
                        )
                    if isinstance(inst.arg_2, OperandPseudo):
                        instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )
                elif isinstance(inst, InstructionUnary):
                    if isinstance(inst.arg_2, OperandPseudo):
                        instructions[func][i].arg_2 = OperandStack(
                            self.generate_stack_pntr(inst.arg_2.value, func)
                        )
        return instructions

    def set_stack_allocation(
        self, instructions: dict[str, list[Instruction]]
    ) -> dict[str, list[Instruction]]:
        # add stack allocation
        for j, func in enumerate(instructions.keys()):
            if func in self.stack_tracker.keys():
                instructions[func].insert(
                    1, InstructionAllocateStack(self.get_function_stack_size(func) - 4)
                )

        return instructions

    def fix_instructions(
        self, instructions: dict[str, list[Instruction]]
    ) -> dict[str, list[Instruction]]:
        for j, func in enumerate(instructions.keys()):
            for i, inst in enumerate(instructions[func]):
                if isinstance(
                    inst, InstructionMov
                ):  # (can't move stack values, need intermediary reg)
                    if isinstance(inst.arg_1, OperandStack) and isinstance(
                        inst.arg_2, OperandStack
                    ):

                        dest = inst.arg_2
                        instructions[func][i].arg_2 = RegR10()
                        instructions[func].insert(i + 1, InstructionMov(RegR10(), dest))
                if isinstance(
                    inst, InstructionIdiv
                ):  # need to move immediate to R10D, then perform idiv on R10D
                    if isinstance(inst.arg_1, OperandImmediate):
                        val = inst.arg_1
                        instructions[func][i].arg_1 = RegR10()
                        instructions[func].insert(i, InstructionMov(val, RegR10()))
                if isinstance(inst, InstructionCmp):

                    if isinstance(inst.arg_1, OperandStack) and isinstance(
                        inst.arg_2, OperandStack
                    ):
                        print("~~~~")
                        print(f"HAD TO DO CLEAN OF CMP {i}")
                        print(self.pretty_print())
                        dest = inst.arg_2
                        instructions[func][i].arg_2 = RegR10()
                        instructions[func].insert(i, InstructionMov(dest, RegR10()))
                        instructions[func][i + 1].arg_2 = RegR10()
                        instructions[func].insert(i + 2, InstructionMov(RegR10(), dest))
                        print(self.pretty_print())
                        print("~~~~")
                    if isinstance(inst.arg_2, OperandImmediate):
                        print("~~~~")
                        print(f"HAD TO DO CLEAN OF CMP {i}")
                        print(self.pretty_print())
                        val = inst.arg_2
                        instructions[func][i].arg_2 = RegR11()
                        instructions[func].insert(i, InstructionMov(val, RegR11()))
                        print(self.pretty_print())
                        print("~~~~")

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
                        instructions[func][i].arg_2 = RegR10()
                        instructions[func].insert(i, InstructionMov(dest, RegR10()))
                        instructions[func][i + 1].arg_2 = RegR10()
                        instructions[func].insert(i + 2, InstructionMov(RegR10(), dest))
                    if isinstance(inst.binary_operator, BinaryOperatorMult):
                        if isinstance(
                            inst.arg_2, OperandStack
                        ):  # can't use memory as operand for imull, need intermediary reg
                            dest = inst.arg_2
                            instructions[func].insert(i, InstructionMov(dest, RegR11()))
                            instructions[func][i + 1].arg_2 = RegR11()
                            instructions[func].insert(
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
                            instructions[func].insert(
                                i,
                                InstructionMov(
                                    src, RegCX()
                                ),  # only cx can be used as shift count
                            )
                            instructions[func].insert(
                                i + 1, InstructionMov(dest, RegR10())
                            )
                            instructions[func][i + 2].arg_1 = RegCX()
                            instructions[func][i + 2].arg_2 = RegR10()
                            instructions[func].insert(
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
                            instructions[func].insert(i, InstructionMov(src, RegCX()))
                            instructions[func].insert(
                                i + 1, InstructionMov(dest, RegR10())
                            )
                            instructions[func][i + 2].arg_1 = RegCX()
                            instructions[func][i + 2].arg_2 = RegR10()
                            instructions[func].insert(
                                i + 3, InstructionMov(RegR10(), dest)
                            )
        return instructions

    def parse(self, tacky: list[IRNode]):

        current_func_identifier = ""
        for i, tack in enumerate(tacky):

            if isinstance(tack, IRProgramNode):
                self.instructions["__PROGRAM__"].append(Program(self.program_name))

            elif isinstance(tack, IRFunctionNode):

                self.instructions[tack.identifier].append(Function(tack.identifier))
                current_func_identifier = tack.identifier
                self.instructions["__PROGRAM__"][0].globalls.append(tack.identifier)

            elif isinstance(tack, IRReturnNode):
                self.instructions[current_func_identifier].extend(
                    self.parse_return(tack)
                )

            elif isinstance(tack, IRUnaryNode):
                self.instructions[current_func_identifier].extend(
                    self.parse_unary(tack)
                )

            elif isinstance(tack, IRBinaryNode):
                self.instructions[current_func_identifier].extend(
                    self.parse_binary(tack)
                )

            elif isinstance(tack, IRJumpIfZeroNode):
                self.instructions[current_func_identifier].extend(
                    [
                        InstructionCmp(
                            OperandImmediate(0), self._parse_operand(tack.condition)
                        ),
                        InstructionJmpCC(ConditionCodeEqual(), tack.target),
                    ]
                )
            elif isinstance(tack, IRJumpIfNotZeroNode):
                self.instructions[current_func_identifier].extend(
                    [
                        InstructionCmp(
                            OperandImmediate(0), self._parse_operand(tack.condition)
                        ),
                        InstructionJmpCC(ConditionCodeNotEqual(), tack.target),
                    ]
                )
            elif isinstance(tack, IRCopyNode):
                self.instructions[current_func_identifier].append(
                    InstructionMov(
                        self._parse_operand(tack.sources[0]),
                        self._parse_operand(tack.dst),
                    )
                )
            elif isinstance(tack, IRJumpNode):
                self.instructions[current_func_identifier].append(
                    InstructionJmp(tack.target)
                )
            elif isinstance(tack, IRLabelNode):
                self.instructions[current_func_identifier].append(
                    InstructionLabel(tack.identifier)
                )

            else:
                raise Exception(f"Unknown IR {tack}")

        self.instructions = self.place_stack(self.instructions)
        self.instructions = self.set_stack_allocation(self.instructions)
        self.instructions = self.fix_instructions(self.instructions)

        return self.instructions

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
