import ast
import astor
import re
import numpy as np

class ImportTransformer(ast.NodeTransformer):
    def __init__(self):
        self.imports = [] # save in the node form
        self.scope_stack = ['module']  # Start at the module level

        self.special_import = ["typing","importlib"]
        self.future_appear = False # if True, `from __future__ import annotations` should be line 1
        self.remained_imports = set() # import should saved, added in the start of module

    @property
    def current_scope(self):
        return self.scope_stack[-1]
    
    def is_special_import(self, module_name):
        if module_name is None:
            return False 
        # Check if the module name matches any entry in special_import
        else:
            return any(module_name.startswith(special) or special.startswith(module_name) for special in self.special_import)
    
    
    def visit_Import(self, node):
        if self.current_scope == 'module':
            for alias in node.names:
                # skip
                if self.is_special_import(alias.name):
                    return node
                
            self.imports.append(node)
            return None
        else:
            return node

    def visit_ImportFrom(self, node):
        if self.current_scope == 'module':
            module_name = node.module

            # deal `import __future specially`
            if module_name == "__future__" and any(alias.name == "annotations" for alias in node.names):
                # Handle special future import
                self.future_appear = True
                return None
            
            if self.is_special_import(module_name):
                # skip
                return node
            
            for alias in node.names:
                if alias.name != '*':
                    self.imports.append(node)
                    return None
            return node # avoid adding `from numpy import *`
        else:
            return node

    def visit_FunctionDef(self, node):
        if hasattr(node, 'processed') and node.processed == True:
            return node
        
        self.scope_stack.append('function')
        
        # Check function arguments for type annotations
        for arg in node.args.args:
            if arg.annotation:
                self._check_annotation(arg.annotation)
        
        # Check default values of arguments
        for default in node.args.defaults:  # Check defaults in function definition
            # self._check_default(default)   
            self._check_annotation(default)             
                
        # Check return annotation
        if node.returns:
            self._check_annotation(node.returns)
        
        # Check function decorators
        for decorator in node.decorator_list:
            self._check_annotation(decorator)
        
        node.body = self._transform_body(node.body)
        
        node.processed = True

        self.generic_visit(node)
        self.scope_stack.pop() # it should exec at the end, after the `generic_visit()`
        
        return node
    # newly added
    def _check_default(self, default):
        """
        Check if the default value uses any imported names and add the necessary imports.
        """
        if isinstance(default, ast.Call):
            # Check if it's a call to a function like np.array
            if isinstance(default.func, ast.Attribute):
                if isinstance(default.func.value, ast.Name):
                    self._add_import_for_name(default.func.value.id)

    def _check_annotation(self, annotation):
        """
        Check if the annotation uses any imported names and add the necessary imports.
        """
        for node in ast.walk(annotation):
            if isinstance(node, ast.Name):
                self._add_import_for_name(node.id)
            elif isinstance(node, ast.Attribute):
                self._add_import_for_name(node.value.id if isinstance(node.value, ast.Name) else None)

    def _add_import_for_name(self, name):
        """
        Add the necessary import for a given name if it exists in self.imports.
        """
        if name == None:
            return 
        for import_node in self.imports:
            if isinstance(import_node, ast.Import):
                for alias in import_node.names:
                    if (alias.name == name or 
                        (alias.asname and alias.asname == name) or 
                        name.startswith(alias.name + ".")):
                        self.remained_imports.add(import_node)
                        return  # The import already exists, no need to add it again
            elif isinstance(import_node, ast.ImportFrom):
                for alias in import_node.names:
                    if (alias.name == name or 
                        (alias.asname and alias.asname == name) or 
                        name.startswith(alias.name + ".")):
                        self.remained_imports.add(import_node)
                        return  # The import already exists, no need to add it again

    def visit_ClassDef(self, node):  # 1.non-top scope
        if hasattr(node, 'processed') and node.processed == True:
            return node
        
        self.scope_stack.append('class')
        
        # Check base classes for imports
        for base in node.bases:
            self._check_annotation(base)
        
        # Check function decorators
        for decorator in node.decorator_list:
            self._check_annotation(decorator)
        
        node.body = self._transform_body(node.body)
        node.processed = True

        self.generic_visit(node)
        self.scope_stack.pop()

        return node

    def visit_If(self, node): # 2.none-top scope

        def handle_orelse(orelse_nodes):
            if not orelse_nodes:
                return []
            if isinstance(orelse_nodes[0], ast.If):
                # This is an elif
                return [self.visit_If(orelse_nodes[0])]
            else:
                # This is an else
                return self._transform_body(orelse_nodes)
            
        
        self.scope_stack.append('if')
        # case1: If is top-level, add to `remained_imports` set
        # case2: none top-level, put ahead of the If statement
        if len(self.scope_stack) == 2: # case 1: top level
            # 1.if condition
            condition_imports = self._check_if_condition(node.test)
            self.remained_imports.update(condition_imports)
            # 2. if body
            node.body = self._transform_body(node.body)
            # 3.else part
            node.orelse = handle_orelse(node.orelse) 
            self.generic_visit(node)
            self.scope_stack.pop()
            return node
        else: # case 2: put import ahead of the If statement
            condition_imports = self._check_if_condition(node.test)
            new_body = []
            new_body.extend(list(condition_imports))

            node.body = self._transform_body(node.body)
            node.orelse = handle_orelse(node.orelse)

            new_body.append(node)
            self.generic_visit(node)
            self.scope_stack.pop()
            return new_body



    
    # for if condition only
    def _check_if_condition(self, condition):
        required_imports = set() # avoid duplicated add
        for node in ast.walk(condition):
            if isinstance(node, ast.Name):
                import_node = self._find_import_for_name(node.id)
                if import_node and import_node not in self.remained_imports:
                    required_imports.add(import_node)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    import_node = self._find_import_for_name(node.value.id)
                    if import_node and import_node not in self.remained_imports:
                        required_imports.add(import_node)

        return required_imports
    
    # for if condition only
    def _find_import_for_name(self, name):
        for import_node in self.imports:
            if isinstance(import_node, ast.Import):
                for alias in import_node.names:
                    if alias.name == name or (alias.asname and alias.asname == name) or (alias.name.startswith(name) and alias.name.find(".") != -1 ) : # deal `import os.path` pattern specially
                        return import_node
            elif isinstance(import_node, ast.ImportFrom):
                for alias in import_node.names:
                    if alias.name == name or (alias.asname and alias.asname == name):
                        return import_node
        return None


    def visit_Try(self, node):# 3.none-top scope
        self.scope_stack.append('try')
        node.body = self._transform_body(node.body)
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_For(self, node): # 4.none-top scope
        self.scope_stack.append('for')
        node.body = self._transform_body(node.body)
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_While(self, node): # 5.none-top scope
        self.scope_stack.append('while')
        node.body = self._transform_body(node.body)
        self.generic_visit(node)
        self.scope_stack.pop()
        return node

    def visit_With(self, node): # 6.none-top scope
        self.scope_stack.append('with')
        node.body = self._transform_body(node.body)
        self.generic_visit(node)
        self.scope_stack.pop()
        return node
    
    # handle the top assign code using package
    def visit_Assign(self, node):
        if self.current_scope == 'module':
            return self._transform_assignment(node)
        # self.generic_visit(node)
        return node
    
    def visit_AnnAssign(self, node):
        if self.current_scope == 'module':
            return self._transform_assignment(node)
        # self.generic_visit(node)
        return node

    def _transform_body(self, body):
        new_body = []
        for stmt in body:
            required_imports = []
            for node in self.imports:
                for alias in node.names: # existing multi `from module import func1, func2, func3`
                    module_use = alias.asname if alias.asname else alias.name
                    if self._uses_import(stmt, module_use):
                        required_imports.append(node)
                        # break #this means only append once
            for node in required_imports:
                new_body.append(node)
                # self.imports.remove(node) # no need to remove, might be used later
            new_body.append(stmt)
        return new_body

    
    def _transform_assignment(self, node):
        """
        Handle assignment statements in top-level modules, check if they use imported modules or objects.
        If used, insert corresponding import statements before the assignment statements.
        """
        new_body = []
        required_imports = []

        for alias_node in self.imports:
            for alias in alias_node.names:
                module_use = alias.asname if alias.asname else alias.name
                if self._uses_import(node, module_use):
                    required_imports.append(alias_node)

        # insert needed import statements
        for nd in required_imports:
            new_body.append(nd)
            # self.imports.remove(nd) # no need to remove

        # add original assignment statement
        new_body.append(node)

        # return multiple nodes if there are statements to insert
        if required_imports:
            return new_body
        return node
    
    def _uses_import(self, node, module_use): # depth = 2
        """
        Recursively check if the current node and its child nodes use the specified module or object
        """
        # special case, when the function node was passed , avoid the outer import
        if isinstance(node, ast.FunctionDef):
            return False
        
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id == module_use:
                return True
            elif isinstance(child, ast.Attribute):
                if self._check_attribute_chain(child, module_use):
                    return True
        return False

    def _check_attribute_chain(self, node, module_use):
        """
        Recursively check if the attribute chain matches the specified module or object
        """
        parts = module_use.split('.')
        return self._match_attribute_chain(node, parts)

    def _match_attribute_chain(self, node, parts):
        """
        Recursively check if the attribute chain matches the specified module path parts
        """
        if not parts:
            return False
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == parts[0]:
                return self._match_attribute_chain(node.attr, parts[1:])
            elif isinstance(node.value, ast.Attribute):
                return self._match_attribute_chain(node.value, parts)
        elif isinstance(node, str) and node == parts[0]:
            return len(parts) == 1
        return False

def transform_code(source_code):
    tree = ast.parse(source_code)
    transformer = ImportTransformer()
    transformer.visit(tree)

    # add the should remain imports
    new_body = []
    if transformer.future_appear:
        new_body.append(ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations", asname=None)], level=0))
    for imp_node in transformer.remained_imports:
        new_body.append(imp_node)
    new_body.extend(tree.body)
    tree.body = new_body
    
    return ast.unparse(tree)
