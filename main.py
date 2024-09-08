# Mostly written by generative AI, see prompts.txt

import sys
import curses


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.expanded = False  # New: track whether the node is expanded

    def add_child(self, child):
        self.children.append(child)

    def toggle(self):
        self.expanded = not self.expanded  # New: toggle expanded/collapsed state

    def __repr__(self, level=0):
        indent = " " * (level * 4)
        result = f"{indent}{self.value} {'[+]' if not self.expanded else '[-]'}\n"
        if self.expanded:
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


def display_tree(stdscr, tree, selected_node):
    stdscr.clear()

    def draw_node(node, level=0, index=0):
        indent = " " * (level * 4)
        symbol = "[+]" if not node.expanded else "[-]"
        line = f"{indent}{node.value} {symbol}"
        if index == selected_node:
            stdscr.addstr(f"> {line}\n", curses.A_REVERSE)
        else:
            stdscr.addstr(f"  {line}\n")
        current_index = index
        if node.expanded:
            for child in node.children:
                current_index = draw_node(child, level + 1, current_index + 1)
        return current_index

    draw_node(tree)
    stdscr.refresh()


def traverse_tree(node, flat_list=None):
    if flat_list is None:
        flat_list = []
    flat_list.append(node)
    if node.expanded:
        for child in node.children:
            traverse_tree(child, flat_list)
    return flat_list


def curses_main(stdscr, root):
    selected_node = 0
    tree_list = traverse_tree(root)  # Start with a flat list

    while True:
        display_tree(stdscr, root, selected_node)

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            selected_node = min(selected_node + 1, len(tree_list) - 1)
        elif key == curses.KEY_UP:
            selected_node = max(selected_node - 1, 0)
        elif key == 10:  # Enter key to toggle expand/collapse
            selected_node_node = tree_list[selected_node]
            selected_node_node.toggle()
            tree_list = traverse_tree(root)  # Re-flatten the tree after toggling

        elif key == ord('q'):  # Quit on 'q'
            break


if __name__ == "__main__":
    # Sample input lines (trimmed of excess whitespace from output)
    lines = open(sys.argv[1]).read().strip().splitlines()

    tree = build_tree(lines)

    # Start curses UI
    curses.wrapper(curses_main, tree)
