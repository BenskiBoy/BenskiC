from parser.ParserConstructs import *
from collections import defaultdict
import copy


class SymbolType:
    def __init__(self, type: str):
        self.type = type

    def __repr__(self):
        return f"SYMBOL_TYPE({self.type})"


class IntSymbolType(SymbolType):
    def __init__(self):
        super().__init__("INT")

    def __repr__(self):
        return super().__repr__()


class FunctionSymbolType(SymbolType):
    def __init__(self, param_count: int, defined: bool = False):
        super().__init__("FUNCTION")
        self.param_count = param_count
        self.defined = defined

    def __eq__(self, other):
        if isinstance(other, FunctionSymbolType):
            return (
                self.param_count == other.param_count and self.defined == other.defined
            )
        return False

    def __repr__(self):
        return (
            f"FUNCTION_SYMBOL(param_count={self.param_count}, defined={self.defined})"
        )


class SemanticAnalysis:
    def __init__(self):
        self.scope_level = 0
        self.identifier_map = defaultdict(dict)
        self.previous_identifier_map = {}
        self.symbol_tree = {}
        self.semantic_analysis_within_function = False

        self.label_declarations = (
            []
        )  # List of declared labels (track incase of multiple declarations)
        self.label_calls = (
            []
        )  # List of called labels (track for incase call a label that doesn't exist)

    def enter_scope(self):
        # Create a new scope
        self.scope_level += 1
        self.previous_identifier_map = copy.deepcopy(self.identifier_map)

        for identifier in self.identifier_map:
            self.identifier_map[identifier]["from_current_scope"] = False

    def exit_scope(self):
        # Remove the current scope

        self.identifier_map = copy.deepcopy(self.previous_identifier_map)

        if self.scope_level > 0:
            self.scope_level -= 1
        else:
            raise Exception("No scope to exit.")

    def make_temporary_variable(self, identifier: str) -> str:
        if identifier in self.identifier_map:
            if (
                self.identifier_map[identifier]["from_current_scope"]
                and not self.identifier_map[identifier]["has_linkage"]
            ):
                raise Exception(
                    f"Variable '{identifier}' already declared in this scope."
                )

        # Create unique name
        unique_name = f"{identifier}.{self.scope_level}"

        # Add to current scope
        self.identifier_map[identifier]["new_name"] = unique_name
        self.identifier_map[identifier]["from_current_scope"] = True
        self.identifier_map[identifier]["has_linkage"] = False

        return unique_name

    def get_temporary_identifier(self, identifier: str) -> str:
        if identifier in self.identifier_map:
            return self.identifier_map[identifier]["new_name"]

        raise Exception(f"Variable '{identifier}' not found in any scope.")

    def parse(self, ast: ProgramNode) -> ProgramNode:
        ast = self.semantic_analysis_parse(ast)
        self.typecheck_parse(ast)

        # Check for label calls
        if self.label_calls:  # check if there are any label calls
            if not bool(set(self.label_declarations) & set(self.label_calls)):
                raise Exception(
                    f"Label name '{set(self.label_declarations) & set(self.label_calls)}' not declared."
                )

        ast = self.resolve_control_flow(ast)

        return ast

    def typecheck_parse(self, ast: ProgramNode) -> ProgramNode:
        for i, function in enumerate(ast.functions):
            function = self.typecheck_function_declaration(function)
        return ast

    def semantic_analysis_parse(self, ast: ProgramNode) -> ProgramNode:
        for i, function in enumerate(ast.functions):  # functions
            ast.functions[i] = self.resolve_declaration(function)
            # self.semantic_analysis_parse_block(function.body)
        return ast

    def semantic_analysis_parse_block(
        self, block: BlockNode, force_current_block: bool = False
    ) -> BlockNode:
        if not force_current_block:
            self.enter_scope()
        for i, item in enumerate(block.children):
            if isinstance(item, BlockItemNode):
                block.children[i] = self.semantic_analysis_parse_block_item(item)
            else:
                raise Exception(f"Unknown block type: {type(item)}")
        if not force_current_block:
            self.exit_scope()
        return block

    def semantic_analysis_parse_block_item(
        self, block_item: BlockItemNode
    ) -> BlockItemNode:
        content = block_item.child
        if isinstance(content, DeclarationNode):
            block_item = self.resolve_declaration(content)
        elif isinstance(content, Statement):
            block_item = self.resolve_statement(content)
        elif isinstance(content, ExpressionNode):
            block_item = self.resolve_expression(content)
        elif isinstance(content, BlockNode):
            block_item = self.semantic_analysis_parse_block(content)
        elif content is None:
            block_item = None
        else:
            raise Exception(f"Unknown block item type {content}.")

        return BlockItemNode(block_item)

    def resolve_function_parameter(self, declaration: str):
        declaration = self.make_temporary_variable(declaration)
        return declaration

    def resolve_declaration(self, declaration: DeclarationNode) -> DeclarationNode:

        if isinstance(declaration, FunctionDeclarationNode):

            self.enter_scope()
            if declaration.identifier in self.identifier_map:
                prev_entry = self.identifier_map[declaration.identifier]
                if prev_entry["from_current_scope"] and (not prev_entry["has_linkage"]):
                    raise Exception("Duplicate Declaration")

            self.identifier_map[declaration.identifier][
                "new_name"
            ] = declaration.identifier
            self.identifier_map[declaration.identifier]["from_current_scope"] = True
            self.identifier_map[declaration.identifier]["has_linkage"] = True

            inner_map = copy.deepcopy(self.identifier_map)
            new_params = []
            for param in declaration.params:
                new_params.append(self.resolve_function_parameter(param))

            new_body = None
            if declaration.body is not None:
                if self.semantic_analysis_within_function:
                    raise Exception(
                        "Function declaration inside another function is not allowed."
                    )
                self.semantic_analysis_within_function = True
                # the parameters are already in the current scope
                # so we don't need to enter a new scope
                new_body = self.semantic_analysis_parse_block(
                    declaration.body, force_current_block=True
                )
                self.semantic_analysis_within_function = False

            self.exit_scope()

            self.identifier_map = inner_map

            return FunctionDeclarationNode(
                self.identifier_map[declaration.identifier]["new_name"],
                new_params,
                new_body,
            )

        elif isinstance(declaration, VariableDeclarationNode):

            if declaration.identifier in self.identifier_map:
                prev_entry = self.identifier_map[declaration.identifier]
                if prev_entry["from_current_scope"] and prev_entry["has_linkage"]:
                    raise Exception(
                        "It's illegal to declare an identifier with external linkage and no linkage in the same scope"
                    )

            declaration.identifier = self.make_temporary_variable(
                declaration.identifier
            )
            if declaration.exp:
                declaration.exp = self.resolve_expression(declaration.exp)

            return declaration
        else:
            raise Exception(f"Unknown declaration type {type(declaration)}.")

    def resolve_statement(self, statement: Statement) -> Statement:
        if statement is None:
            return None
        elif isinstance(statement, ReturnNode):
            statement.exp = self.resolve_expression(statement.exp)
            return statement
        elif isinstance(statement, IfNode):
            statement.condition = self.resolve_expression(statement.condition)
            statement.then = self.resolve_statement(statement.then)
            if statement.else_:
                statement.else_ = self.resolve_statement(statement.else_)

            return statement
        elif isinstance(statement, WhileNode):
            statement.condition = self.resolve_expression(statement.condition)
            statement.body = self.resolve_statement(statement.body)
            return statement
        elif isinstance(statement, DoWhileNode):
            statement.body = self.resolve_statement(statement.body)
            statement.condition = self.resolve_expression(statement.condition)
            return statement
        elif isinstance(statement, ForNode):
            self.enter_scope()
            init = None
            if statement.init:
                init = self._resolve_for_init(statement.init)
            condition = None
            if statement.condition:
                condition = self.resolve_expression(statement.condition)
            post = None
            if statement.post:
                post = self.resolve_expression(statement.post)
            body = self.resolve_statement(statement.body)
            self.exit_scope()
            return ForNode(body, init, condition, post)
        elif isinstance(statement, ConditionalNode):
            statement.condition = self.resolve_expression(statement.condition)
            statement.then = self.resolve_statement(statement.then)
            statement.else_ = self.resolve_statement(statement.else_)
            return statement
        elif isinstance(statement, GotoNode):
            self.label_calls.append(statement.label)
        elif isinstance(statement, BlockNode):
            statement = self.semantic_analysis_parse_block(statement)
            return statement
        elif isinstance(statement, LabeledStatementNode):
            label = statement.label
            if statement.label in self.label_declarations:
                raise Exception(f"Label '{statement.label}' already called.")
            self.label_declarations.append(statement.label)
            return LabeledStatementNode(
                label,
                self.resolve_statement(statement.child),
            )
        elif isinstance(statement, GotoNode):
            self.label_calls.append(statement.label)
            return GotoNode(statement.label)
        elif isinstance(statement, ExpressionNode):
            statement = self.resolve_expression(statement)
            return statement
        elif isinstance(statement, BreakNode):
            return BreakNode()
        elif isinstance(statement, ContinueNode):
            return ContinueNode()
        elif isinstance(statement, SwitchNode):
            statement.condition = self.resolve_expression(statement.condition)
            statement.body = self.resolve_statement(statement.body)
            return statement
        elif isinstance(statement, CaseNode):
            if not isinstance(statement.condition, ConstantNode):
                raise Exception("Case condition must be a constant value")
            statement.condition = self.resolve_expression(statement.condition)
            for i, body in enumerate(statement.body):
                if isinstance(body, BlockItemNode):
                    body = body.child
                if isinstance(body, DeclarationNode):
                    statement.body[i] = self.resolve_declaration(body)
                else:
                    statement.body[i] = self.resolve_statement(body)
            return statement
        elif isinstance(statement, DefaultNode):
            if self.label_calls.count(statement.label) > 1:
                raise Exception("Multiple default statements in switch")
            for i, body in enumerate(statement.body):
                statement.body[i] = self.resolve_statement(body)
            return statement
        elif isinstance(statement.child, DeclarationNode):
            statement.child = self.resolve_declaration(statement.child)

        return statement

    def resolve_expression(self, expression: ExpressionNode) -> ExpressionNode:
        if expression is None:
            return None
        elif isinstance(expression, ConstantNode):
            return expression
        elif isinstance(expression, VarNode):
            return VarNode(self.get_temporary_identifier(expression.identifier))
        elif isinstance(expression, AssignmentNode):
            if not isinstance(expression.lvalue, VarNode):
                raise Exception("Left side of assignment must be a variable.")
            expression.lvalue = self.resolve_expression(expression.lvalue)
            expression.rvalue = self.resolve_expression(expression.rvalue)
            return expression
        elif isinstance(expression, BinaryNode):
            expression.exp_1 = self.resolve_expression(expression.exp_1)
            expression.exp_2 = self.resolve_expression(expression.exp_2)
            return expression
        elif isinstance(expression, UnaryNode):
            child = self.resolve_expression(expression.exp)

            if isinstance(child, UnaryNode) and isinstance(expression, UnaryNode):
                if expression.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ] and child.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ]:
                    raise Exception(
                        "Increment/Decrement operator cannot be used on itself."
                    )
            if isinstance(child, AssignmentNode) and isinstance(
                expression.operator, UnaryOperatorNode
            ):
                raise Exception("Unary operator cannot be used on assignment.")
            if isinstance(child, (ConstantNode, BinaryNode)) and isinstance(
                expression, UnaryNode
            ):
                if expression.operator in [
                    UnaryOperatorNode.INCREMENT,
                    UnaryOperatorNode.DECREMENT,
                ]:
                    raise Exception(
                        "Unary operator cannot be used on constant or binary node."
                    )
            return UnaryNode(child, expression.operator, expression.postfix)
        elif isinstance(expression, ConditionalNode):
            expression.condition = self.resolve_expression(expression.condition)
            expression.then = self.resolve_expression(expression.then)
            expression.else_ = self.resolve_expression(expression.else_)
            return expression

        elif isinstance(expression, FunctionCallNode):

            if expression.identifier in self.identifier_map:
                new_fun_name = self.identifier_map[expression.identifier]["new_name"]
                new_args = []
                for arg in expression.arguments:
                    new_args.append(self.resolve_expression(arg))
                return FunctionCallNode(new_fun_name, new_args)
            else:
                raise Exception("Undeclared Function")

        else:
            raise Exception(f"Unknown expression type {type(expression)}.")

    def _resolve_for_init(
        self, init: InitDeclNode | InitExprNode
    ) -> InitDeclNode | InitExprNode:
        if isinstance(init, InitDeclNode):
            return InitDeclNode(
                self.resolve_declaration(init.declaration),
                init.label,
            )
        elif isinstance(init, InitExprNode):
            return InitExprNode(
                self.resolve_expression(init.expression),
                init.label,
            )
        else:
            raise Exception(f"Unknown for loop initialization type {type(init)}.")

    ##################### TYPE CHECKING ########################
    def typecheck_exp(self, expression: ExpressionNode):
        print(f"Typechecking expression: {expression}")
        if isinstance(expression, FunctionCallNode):
            f_type = self.symbol_tree[expression.identifier]
            if isinstance(f_type, IntSymbolType):
                raise Exception("Variable used as function name")
            elif f_type.param_count != len(expression.arguments):
                raise Exception(
                    f"Function {expression.identifier} called with the wrong number of args, got {len(expression.arguments)}, expected {len(f_type.param_count)}"
                )
            for arg in expression.arguments:
                self.typecheck_exp(arg)
        elif isinstance(expression, VarNode):
            if self.symbol_tree[expression.identifier].type != "INT":
                raise Exception("Function name used as variable")
        elif isinstance(expression, AssignmentNode):
            self.typecheck_exp(expression.rvalue)
            self.typecheck_exp(expression.lvalue)
        elif isinstance(expression, BinaryNode):
            self.typecheck_exp(expression.exp_1)
            self.typecheck_exp(expression.exp_2)
        elif isinstance(expression, UnaryNode):
            self.typecheck_exp(expression.exp)
        elif isinstance(expression, ConditionalNode):
            self.typecheck_exp(expression.condition)
            self.typecheck_exp(expression.then)
            self.typecheck_exp(expression.else_)
        elif isinstance(expression, ConstantNode):
            pass

    def typecheck_variable_declaration(self, declaration: VariableDeclarationNode):
        self.symbol_tree[declaration.identifier] = IntSymbolType()
        if declaration.exp:
            self.typecheck_exp(declaration.exp)

    def typecheck_function_declaration(self, declaration):
        function_type = FunctionSymbolType(len(declaration.params))
        has_body = declaration.body is not None
        already_defined = False
        if declaration.identifier in self.symbol_tree:
            old_declaration = self.symbol_tree[declaration.identifier]
            if old_declaration != function_type:
                raise Exception(
                    f"Function name '{declaration.identifier}' used as variable."
                )
            already_defined = old_declaration.defined
            if already_defined and has_body:
                raise Exception(f"Function '{declaration.identifier}' already defined.")
        self.symbol_tree[declaration.identifier] = FunctionSymbolType(
            len(declaration.params), already_defined or has_body
        )

        if has_body:
            for param in declaration.params:
                self.symbol_tree[param] = IntSymbolType()
            self.typecheck_block(declaration.body)

    def typecheck_block(self, block: BlockNode):
        for item in block.children:
            if isinstance(item, BlockItemNode):
                if isinstance(item.child, VariableDeclarationNode):
                    self.typecheck_variable_declaration(item.child)
                elif isinstance(item.child, FunctionDeclarationNode):
                    self.typecheck_function_declaration(item.child)
                elif isinstance(item.child, ExpressionNode):
                    self.typecheck_exp(item.child)
                elif isinstance(item.child, Statement):
                    self.typecheck_statement(item.child)
                elif isinstance(item.child, BlockNode):
                    self.typecheck_block(item.child)
            else:
                raise Exception(f"Unknown block item type {item}.")

    def typecheck_statement(self, statement: Statement):
        if isinstance(statement, ReturnNode):
            self.typecheck_exp(statement.exp)
        elif isinstance(statement, IfNode):
            self.typecheck_exp(statement.condition)
            self.typecheck_statement(statement.then)
            if statement.else_:
                self.typecheck_statement(statement.else_)
        elif isinstance(statement, WhileNode):
            self.typecheck_exp(statement.condition)
            self.typecheck_statement(statement.body)
        elif isinstance(statement, DoWhileNode):
            self.typecheck_statement(statement.body)
            self.typecheck_exp(statement.condition)
        elif isinstance(statement, ForNode):
            if statement.init:
                if isinstance(statement.init, InitDeclNode):
                    self.typecheck_variable_declaration(statement.init.declaration)
                elif isinstance(statement.init, InitExprNode):
                    self.typecheck_exp(statement.init.expression)
                else:
                    raise Exception("For loop init must be a variable declaration")
            if statement.condition:
                self.typecheck_exp(statement.condition)
            if statement.post:
                self.typecheck_exp(statement.post)
            self.typecheck_statement(statement.body)
        elif isinstance(statement, SwitchNode):
            self.typecheck_exp(statement.condition)
            self.typecheck_statement(statement.body)
        elif isinstance(statement, CaseNode):
            for body in statement.body:
                if isinstance(body, BlockItemNode):
                    body = body.child
                if isinstance(body, DeclarationNode):
                    self.typecheck_variable_declaration(body)
                else:
                    self.typecheck_statement(body)
        elif isinstance(statement, DefaultNode):
            for body in statement.body:
                if isinstance(body, BlockItemNode):
                    body = body.child
                if isinstance(body, DeclarationNode):
                    self.typecheck_variable_declaration(body)
                else:
                    self.typecheck_statement(body)

    ##################### CONTROL FLOW ########################
    def resolve_control_flow(self, ast: ProgramNode) -> ProgramNode:
        self.control_flow_count = 0
        self.control_flow_stack = []

        self.current_switch_case_targets = (
            []
        )  # List of case labels for the current switch
        self.current_switch_default_target = False
        self.switch_depth = (
            0  # Track the depth of nested switches, used to ensure case within a switch
        )
        self.switch_case_values = (
            {}
        )  # Track case values for each switch, used to ensure no duplicates

        # Start the recursive traversal
        if isinstance(ast, ProgramNode):
            for i, function in enumerate(ast.functions):
                ast.functions[i] = self._resolve_control_flow_node(function)

        return ast

    def _resolve_control_flow_node(self, node):
        if isinstance(node, FunctionDeclarationNode):
            node.body = self._resolve_control_flow_node(node.body)

        if isinstance(node, LabeledStatementNode):
            # Process the child statement
            node.child = self._resolve_control_flow_node(node.child)

        elif isinstance(node, WhileNode):
            loop_label = f"_WHILE_LOOP_{self.control_flow_count}"
            self.control_flow_count += 1
            self.control_flow_stack.append(("loop", loop_label))

            node.body = self._resolve_control_flow_node(node.body)

            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, ForNode):
            loop_label = f"_FOR_LOOP_{self.control_flow_count}"
            self.control_flow_count += 1
            self.control_flow_stack.append(("loop", loop_label))

            node.body = self._resolve_control_flow_node(node.body)
            if node.init:
                node.init = self._resolve_control_flow_node(node.init)

            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, DoWhileNode):
            loop_label = f"_DO_WHILE_{self.control_flow_count}"
            self.control_flow_count += 1
            self.control_flow_stack.append(("loop", loop_label))

            node.body = self._resolve_control_flow_node(node.body)

            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, BreakNode):
            # Find the nearest enclosing structure of any type (loop or switch)
            if not self.control_flow_stack:
                raise Exception("Break statement not within loop or switch")

            # Get label of nearest enclosing structure
            structure_type, label = self.control_flow_stack[-1]
            node.label = label
            node.target_type = structure_type  # Store the type for code generation

        elif isinstance(node, ContinueNode):
            # Continue can only target loops, not switches
            # Find the nearest enclosing loop
            loop_context = next(
                (ctx for ctx in reversed(self.control_flow_stack) if ctx[0] == "loop"),
                None,
            )

            if not loop_context:
                raise Exception("Continue statement not within loop")

            # Get label of nearest enclosing loop
            _, label = loop_context
            node.label = label

        elif isinstance(node, BlockNode):
            for i, child in enumerate(node.children):
                if isinstance(child, BlockItemNode):
                    child.child = self._resolve_control_flow_node(child.child)
                else:
                    node.children[i] = self._resolve_control_flow_node(child)

        elif isinstance(node, IfNode):
            node.then = self._resolve_control_flow_node(node.then)
            if node.else_:
                node.else_ = self._resolve_control_flow_node(node.else_)

        elif isinstance(node, BlockItemNode):
            node.child = self._resolve_control_flow_node(node.child)

        elif isinstance(node, CaseNode):

            if self.switch_depth == 0:
                raise Exception("Case statement not within a switch statement")

            if not isinstance(node.condition, ConstantNode):
                raise Exception("Case condition must be a constant value")

            # For constant values, check for duplicates
            if node.condition.value in self.switch_case_values[self.switch_depth - 1]:
                raise Exception(f"Duplicate case value: {node.condition.value}")
            # Record this case value for the current switch
            self.switch_case_values[self.switch_depth - 1].append(node.condition.value)

            # Just process the body, don't push onto the stack
            for i, body in enumerate(node.body):
                node.body[i] = self._resolve_control_flow_node(body)

            # Create a unique label for this case
            case_label = f"_CASE_{self.control_flow_count}"
            self.control_flow_count += 1
            node.label = case_label

            self.current_switch_case_targets[-1].append(case_label)

        elif isinstance(node, DefaultNode):

            if self.switch_depth == 0:
                raise Exception("Default statement not within a switch statement")

            if self.current_switch_default_target:
                raise Exception("Multiple default statements in switch")

            # Just process the body, don't push onto the stack
            for i, body in enumerate(node.body):
                node.body[i] = self._resolve_control_flow_node(body)

            # Create a unique label for this default
            default_label = f"_DEFAULT_{self.control_flow_count}"
            self.control_flow_count += 1
            node.label = default_label
            self.current_switch_default_target = default_label

        elif isinstance(node, SwitchNode):
            # Entering switch
            switch_label = f"_SWITCH_{self.control_flow_count}"
            self.control_flow_count += 1
            self.control_flow_stack.append(("switch", switch_label))

            self.current_switch_case_targets.append([])
            self.switch_depth += 1
            self.switch_case_values[self.switch_depth - 1] = []

            node.condition = self._resolve_control_flow_node(node.condition)
            node.body = self._resolve_control_flow_node(node.body)

            # add the current switch case targets and default target
            node.case_targets = self.current_switch_case_targets[-1]
            if self.current_switch_default_target:
                node.default_target = self.current_switch_default_target

            # Clear the case values for this switch level
            self.current_switch_case_targets = self.current_switch_case_targets[:-1]
            self.current_switch_default_target = None
            self.switch_depth -= 1
            self.switch_case_values[self.switch_depth - 1] = []

            # Assign label and pop from stack
            node.label = switch_label
            self.control_flow_stack.pop()

            # raise Exception(f"Unknown node type {type(node)}.")

        return node
