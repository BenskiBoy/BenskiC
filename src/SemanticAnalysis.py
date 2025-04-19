from parser.ParserConstructs import *
from collections import defaultdict


class SemanticAnalysis:
    def __init__(self):
        self.variable_scopes = [
            {}
        ]  # Stack of scopes - each is a dict mapping original names to unique names
        self.scope_level = 0
        self.all_declarations = (
            set()
        )  # Track all declarations across all scopes for error reporting
        self.original_variable_names = []
        self.label_declarations = []
        self.label_calls = []

    def enter_scope(self):
        """Create a new variable scope when entering a block."""
        self.variable_scopes.append({})
        self.scope_level += 1

    def exit_scope(self):
        """Exit the current scope, but keep track of all declarations for error reporting."""
        # Before we pop, record all declarations from this scope in all_declarations
        for var in self.variable_scopes[-1]:
            self.all_declarations.add(var)

        # Now pop the scope
        self.variable_scopes.pop()
        self.scope_level -= 1

    def make_temporary_identifier(self, identifier: str, add_to_scope=True) -> str:

        current_scope = self.variable_scopes[-1]

        # Check if variable already exists in current scope
        if identifier in current_scope:
            raise Exception(f"Variable '{identifier}' already declared in this scope.")

        # Create unique name
        unique_name = f"{identifier}.{self.scope_level}"

        # Add to current scope if requested
        if add_to_scope:
            current_scope[identifier] = unique_name
            self.original_variable_names.append(identifier)

        return unique_name

    def get_temporary_identifier(self, identifier: str) -> str:
        for scope in reversed(range(self.scope_level + 1)):
            if identifier in self.variable_scopes[scope]:
                return f"{identifier}.{scope}"  # self.variable_map[scope][identifier]

        raise Exception(f"Variable '{identifier}' not declared.")

    def parse(self, ast: ProgramNode) -> ProgramNode:
        ast = self.semantic_analysis_parse(ast)
        ast = self.resolve_control_flow(ast)

        return ast

    def semantic_analysis_parse(self, ast: ProgramNode) -> ProgramNode:
        if isinstance(ast, ProgramNode):
            for i, function in enumerate(ast.functions):
                if isinstance(function, FunctionNode):
                    ast.functions[0] = self.semantic_analysis_parse(function)

        elif isinstance(ast, FunctionNode):
            self.body = self.parse_block(ast.body)

        if self.label_calls:  # check if there are any label calls
            if not bool(set(self.label_declarations) & set(self.label_calls)):
                raise Exception(
                    f"Label name '{set(self.label_declarations) & set(self.label_calls)}' not declared."
                )

        return ast

    def resolve_control_flow(self, ast: ProgramNode) -> ProgramNode:
        """Unified method to handle loop and switch structures for break/continue."""
        self.control_flow_count = 0
        self.control_flow_stack = []

        # Start the recursive traversal
        if isinstance(ast, ProgramNode):
            for i, function in enumerate(ast.functions):
                ast.functions[i] = self._resolve_control_flow_node(function)

        return ast

    def _resolve_control_flow_node(self, node):
        """Process a single node during control flow analysis."""

        if not hasattr(self, "switch_depth"):
            self.switch_depth = 0
        if not hasattr(self, "current_switch_case_targets"):
            self.current_switch_case_targets = []
        if not hasattr(self, "current_switch_default_target"):
            self.current_switch_default_target = []

        if node is None:
            return None

        # Handle different node types
        if isinstance(node, FunctionNode):
            node.body = self._resolve_control_flow_node(node.body)

        if isinstance(node, LabeledStatementNode):
            # Process the child statement
            node.child = self._resolve_control_flow_node(node.child)

        elif isinstance(node, WhileNode):
            # Create a unique label for this loop
            loop_label = f"_WHILE_LOOP_{self.control_flow_count}"
            self.control_flow_count += 1

            # Push this loop onto the stack - noting it's a loop type
            self.control_flow_stack.append(("loop", loop_label))

            # Process loop body
            node.body = self._resolve_control_flow_node(node.body)

            # Assign label and pop from stack
            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, ForNode):
            # Similar handling for for loops
            loop_label = f"_FOR_LOOP_{self.control_flow_count}"
            self.control_flow_count += 1

            # Push as loop type
            self.control_flow_stack.append(("loop", loop_label))

            node.body = self._resolve_control_flow_node(node.body)
            if node.init:
                node.init = self._resolve_control_flow_node(node.init)

            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, DoWhileNode):
            # Similar handling for do-while loops
            loop_label = f"_DO_WHILE_{self.control_flow_count}"
            self.control_flow_count += 1

            # Push as loop type
            self.control_flow_stack.append(("loop", loop_label))

            node.body = self._resolve_control_flow_node(node.body)

            node.label = loop_label
            self.control_flow_stack.pop()

        elif isinstance(node, SwitchNode):
            # Create a unique label for this switch
            switch_label = f"_SWITCH_{self.control_flow_count}"
            self.control_flow_count += 1
            self.switch_depth += 1

            self.current_switch_case_targets.append([])
            self.current_switch_default_target.append(None)

            # Push this switch onto the stack - noting it's a switch type
            self.control_flow_stack.append(("switch", switch_label))

            for i, element in enumerate(node.body.children):
                node.body.children[i] = self._resolve_control_flow_node(element)

            node.case_targets = self.current_switch_case_targets[-1]
            if self.current_switch_default_target:
                node.default_target = self.current_switch_default_target[-1]

            self.current_switch_case_targets = self.current_switch_case_targets[:-1]
            if self.current_switch_default_target:
                self.current_switch_default_target = self.current_switch_default_target[
                    :-1
                ]
            self.switch_depth -= 1

            # Assign label and pop from stack
            node.label = switch_label
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

        # Continue with other node types...
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
            # Just process the body, don't push onto the stack
            for i, body in enumerate(node.body):
                node.body[i] = self._resolve_control_flow_node(body)

            # Create a unique label for this case
            case_label = f"_CASE_{self.control_flow_count}"
            self.control_flow_count += 1
            node.label = case_label
            self.current_switch_case_targets[self.switch_depth - 1].append(case_label)

        elif isinstance(node, DefaultNode):
            # Just process the body, don't push onto the stack
            for i, body in enumerate(node.body):
                node.body[i] = self._resolve_control_flow_node(body)

            # assert no continue in default
            for i, body in enumerate(node.body):
                if isinstance(body, ContinueNode):
                    raise Exception("Continue statement not within loop")

            # Create a unique label for this default
            default_label = f"_DEFAULT_{self.control_flow_count}"
            self.control_flow_count += 1
            node.label = default_label
            self.current_switch_default_target[self.switch_depth - 1] = default_label

        # Don't forget to return the possibly modified node
        return node

    def parse_block(self, block: BlockNode) -> BlockNode:
        self.enter_scope()
        for i, block_item in enumerate(block.children):
            block.children[i] = self.parse_block_item(block_item)
        self.exit_scope()
        return block

    def parse_block_item(self, block: BlockItemNode) -> BlockItemNode:

        content = block.child
        if isinstance(content, DeclarationNode):
            return BlockItemNode(self.resolve_declaration(content))
        elif (
            isinstance(content, ReturnNode)
            or isinstance(block, ExpressionNode)
            or isinstance(content, IfNode)
            or isinstance(content, LabeledStatementNode)
            or isinstance(content, WhileNode)
            or isinstance(content, DoWhileNode)
            or isinstance(content, ForNode)
            or isinstance(content, BreakNode)
            or isinstance(content, ContinueNode)
            or isinstance(content, SwitchNode)
            or isinstance(content, CaseNode)
            or isinstance(content, DefaultNode)
        ):  # statement
            return BlockItemNode(self.resolve_statement(content))
        elif isinstance(content, ExpressionNode):
            return BlockItemNode(self.resolve_expression(content))
        elif content is None:
            return BlockItemNode(None)
        elif isinstance(content, GotoNode):
            self.label_calls.append(content.label)
            return BlockItemNode(content)
        elif isinstance(content, BlockNode):
            block = self.parse_block(content)
            return BlockItemNode(block)
        elif isinstance(content, DeclarationNode):
            return BlockItemNode(self.resolve_declaration(content))
        else:
            raise Exception(f"Unknown block item type {content}.")

    def resolve_declaration(self, declaration: DeclarationNode) -> DeclarationNode:

        unique_name = self.make_temporary_identifier(declaration.identifier)

        # Resolve the initialization expression (if any)
        resolved_exp = None
        if declaration.exp is not None:
            resolved_exp = self.resolve_expression(declaration.exp)

        # Variable is already added to current scope
        self.original_variable_names.append(declaration.identifier)

        return DeclarationNode(unique_name, resolved_exp)

    def resolve_statement(self, statement: Statement) -> Statement:

        # Add switch depth tracking if not already present
        if not hasattr(self, "switch_depth"):
            self.switch_depth = 0

        if not hasattr(self, "switch_case_values"):
            self.switch_case_values = [{}] * 10  # TODO make this dynamic

        if not hasattr(self, "default_reached"):
            self.default_reached = [{}] * 10  # TODO make this dynamic

        if isinstance(statement, BlockNode):
            self.enter_scope()
            for i, block_item in enumerate(statement.children):
                statement.children[i] = self.parse_block_item(block_item)
            self.exit_scope()
            return statement

        elif isinstance(statement, ReturnNode):
            return ReturnNode(self.resolve_expression(statement.exp))

        elif isinstance(statement, LabeledStatementNode):
            label = statement.label
            if statement.label in self.label_declarations:
                raise Exception(f"Label '{statement.label}' already called.")
            self.label_declarations.append(statement.label)
            return LabeledStatementNode(
                label,
                self.resolve_statement(statement.child),
            )

        elif isinstance(statement, IfNode):
            condition = self.resolve_expression(statement.condition)
            then = self.resolve_statement(statement.then)
            else_ = (
                self.resolve_statement(statement.else_)
                if statement.else_ is not None
                else None
            )
            return IfNode(condition, then, else_)
        elif isinstance(statement, AssignmentNode):
            if self.resolve_expression(statement.rvalue) in self.label_declarations:
                raise Exception(
                    f"Label '{expression.rvalue.identifier}' cannot be used as an expression."
                )
            return AssignmentNode(
                self.resolve_expression(statement.lvalue),
                self.resolve_expression(statement.rvalue),
                statement.type,
            )
        elif isinstance(statement, GotoNode):
            self.label_calls.append(statement.label)
            return GotoNode(statement.label)

        elif statement is None:
            return None

        elif isinstance(statement, WhileNode):
            condition = self.resolve_expression(statement.condition)
            body = self.resolve_statement(statement.body)
            return WhileNode(condition, body)

        elif isinstance(statement, DoWhileNode):
            body = self.resolve_statement(statement.body)
            condition = self.resolve_expression(statement.condition)
            return DoWhileNode(condition, body)

        elif isinstance(statement, BreakNode):
            return BreakNode()

        elif isinstance(statement, ContinueNode):
            return ContinueNode()

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

        elif isinstance(statement, SwitchNode):
            self.switch_depth += 1  # Entering switch
            self.enter_scope()
            self.default_reached = [{}] * 10

            statement.condition = self.resolve_expression(statement.condition)

            # Clear the case values for this switch level
            self.switch_case_values[self.switch_depth - 1] = {}

            statement.body = self.resolve_statement(statement.body)

            self.exit_scope()
            self.switch_depth -= 1  # Exiting switch

            return statement

        elif isinstance(statement, CaseNode):
            if self.switch_depth == 0:
                raise Exception("Case statement not within a switch statement")

            if not isinstance(statement.condition, ConstantNode):
                raise Exception("Case condition must be a constant value")

            condition = self.resolve_expression(statement.condition)

            # For constant values, check for duplicates
            if isinstance(condition, ConstantNode):
                value = condition.value
                current_switch_cases = self.switch_case_values[self.switch_depth - 1]

                if value in current_switch_cases:
                    raise Exception(f"Duplicate case value: {value}")

                # Record this case value for the current switch
                current_switch_cases[value] = True

            for i, body in enumerate(statement.body):
                if isinstance(body, BlockItemNode):
                    body = body.child
                if isinstance(body, DeclarationNode):
                    statement.body[i] = self.resolve_declaration(body)
                else:
                    statement.body[i] = self.resolve_statement(body)
            return CaseNode(condition, statement.body)

        elif isinstance(statement, DefaultNode):
            if self.switch_depth == 0:
                raise Exception("Default statement not within a switch statement")

            if self.default_reached[self.switch_depth]:
                raise Exception("Multiple default statements in switch")
            self.default_reached[self.switch_depth] = (
                True  # Only one default allowed, set flag
            )

            for i, body in enumerate(statement.body):
                statement.body[i] = self.resolve_statement(body)
            return DefaultNode(statement.body)

        elif isinstance(statement, ExpressionNode):
            return self.resolve_expression(statement)

        elif isinstance(statement.child, ExpressionNode):
            expression = self.resolve_expression(statement.child)
            return expression

        else:
            raise Exception(f"Unknown statement type {type(statement)}.")

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

    def resolve_expression(self, expression: ExpressionNode) -> ExpressionNode:

        print(f"resolving expression {repr(expression)}")
        if isinstance(expression, VarNode):
            return VarNode(self.get_temporary_identifier(expression.identifier))
        elif isinstance(
            expression,
            AssignmentNode,
        ):
            if not isinstance(expression.lvalue, VarNode):
                raise Exception("Left side of assignment must be a variable.")
            return AssignmentNode(
                self.resolve_expression(expression.lvalue),
                self.resolve_expression(expression.rvalue),
                expression.type,
            )
        elif isinstance(expression, BinaryNode):
            left = self.resolve_expression(expression.exp_1)
            right = self.resolve_expression(expression.exp_2)
            return BinaryNode(
                expression.operator,
                left,
                right,
            )
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
            condition = self.resolve_expression(expression.condition)
            true_exp = self.resolve_expression(expression.then)
            false_exp = self.resolve_expression(expression.else_)
            return ConditionalNode(condition, true_exp, false_exp)

        else:
            return expression
