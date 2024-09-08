# Mostly written by generative AI, see prompts.txt

import sys

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self, level=0):
        indent = " " * (level * 4)
        result = f"{indent}{self.value}\n"
        for child in self.children:
            result += child.__repr__(level + 1)
        return result


def parse_line(line):
    # Separate the "first half" and "second half"
    first_half = ""
    second_half = ""
    in_second_half = False

    for char in line:
        if not in_second_half:
            # Check for unexpected characters in the "first half"
            if char.isalnum() or char == '@':
                in_second_half = True
                second_half += char
            elif char in ' ├─└│┬':
                first_half += char
            else:
                raise ValueError(f"Unexpected character in the first half: {char}")
        else:
            # Check for unexpected characters in the "second half"
            if char.isprintable():
                second_half += char
            else:
                raise ValueError(f"Unexpected character in the second half: {char}")

    return len(first_half), second_half.strip()


def build_tree(lines):
    root = TreeNode("root")
    node_stack = [(root, -1)]  # Stack holds tuples of (TreeNode, indent_level)

    for line in lines:
        indent, value = parse_line(line)

        # Remove nodes from the stack that are no longer parents for this level
        while node_stack and node_stack[-1][1] >= indent:
            node_stack.pop()

        # Create new node and add it to the current parent node
        new_node = TreeNode(value)
        node_stack[-1][0].add_child(new_node)

        # Push the new node onto the stack
        node_stack.append((new_node, indent))

    return root


if __name__ == "__main__":
    # Sample input lines (trimmed of excess whitespace from output)
    lines = open(sys.argv[1]).read().strip().splitlines()

    tree = build_tree(lines)
    print(tree)
