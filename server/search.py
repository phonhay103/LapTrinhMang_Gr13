import os
import pickle
from config import *
from anytree import Node, RenderTree, Resolver, find, LevelOrderIter

def _get_node_path(node):
    path = str(node.path[-1]).split("'")[1] # Get path
    path = path[1:] # Remove '/' at 0

    return path

def create_tree(data_dir='data'):
    tree = Node(data_dir, title='root')
    resolver = Resolver('name')

    for root, dirs, files in os.walk('data'):
        root = '/' + root.replace('\\', '/')
        files = [f.split('.')[0] for f in files]
        r = resolver.get(tree, root)

        # File | Folder with file
        for file in files:
            node = Node(file, parent=r, title="Nan")
            path = _get_node_path(node)
            with open(path + '.' + EXT, 'r') as f:
                title = f.readline().rstrip()
                if not title:
                    title = file
                node.title = title

        # Folder only
        for folder in set(dirs)-set(files):
            node = Node(folder, parent=r, title=folder)

    # Remove emtpy folder
    for i in LevelOrderIter(tree):
        path = _get_node_path(i)
        if os.path.isdir(path) and not os.listdir(path):
            i.parent = None
            del i

    return tree

def _get_indexes_list(node):
    lst = node.children
    lst = [(c.name, c.title) for c in lst]
    if node.parent:
        add_node = (node.parent.name, 'parent')
    else:
        add_node = (None, 'root')
    lst = [add_node] + lst
    return lst

def _get_file_content(node):
    path = _get_node_path(node) + '.' + EXT
    with open(path, 'r') as f:
        data = [line.rstrip() for line in f.readlines()]
    return data

def search_for_index(tree, name):
    node = find(tree, lambda node: node.name == name)
    indexes = _get_indexes_list(node)
    if tree.name == name:
        contents = []
    else:
        contents = _get_file_content(node)
    return pickle.dumps(['110', contents, indexes])