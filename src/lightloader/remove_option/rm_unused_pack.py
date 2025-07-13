import ast
import astor

def find_unused_imports(file_content):
    tree = ast.parse(file_content)
    imports = set()
    used_names = set()

    class ImportFinder(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                imports.add(alias.asname or alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                imports.add(alias.asname or alias.name)
            self.generic_visit(node)

    class NameFinder(ast.NodeVisitor):
        def visit_Name(self, node):
            used_names.add(node.id)
            self.generic_visit(node)

        def visit_Attribute(self, node):
            # recursively visit attribute chain
            self.visit(node.value)

    import_finder = ImportFinder()
    import_finder.visit(tree)

    name_finder = NameFinder()
    name_finder.visit(tree)

    unused_imports = imports - used_names
    return unused_imports

def remove_unused_imports(file_content):
    tree = ast.parse(file_content)
    unused_imports = find_unused_imports(file_content)

    class ImportRemover(ast.NodeTransformer):
        def visit_Import(self, node):
            new_names = [alias for alias in node.names if (alias.asname or alias.name) not in unused_imports]
            if new_names:
                node.names = new_names
                return node
            return None  # Remove entire import statement

        def visit_ImportFrom(self, node):
            new_names = [alias for alias in node.names if (alias.asname or alias.name) not in unused_imports]
            if new_names:
                node.names = new_names
                return node
            return None

    remover = ImportRemover()
    new_tree = remover.visit(tree)
    return astor.to_source(new_tree)
