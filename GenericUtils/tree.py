class Tree:

	def __init__(self, data=None, children=None):
		if children is None:
			children = []
		self.data = data
		self.children = list(children)

	def insert_node(self, data, children=None):
		if isinstance(data, Tree):
			self.children.append(data)
		elif children is not None:
			self.children.append(Tree(data, children))
		else:
			self.children.append(Tree(data))
		return self

	def get_tree(self):
		return self

	def __str__(self):
		return f"({self.data.__class__})\n[{','.join([str(c) for c in self.children])}]"


def find_parent_of_node(to_search: Tree, to_find_parent_of: Tree):
	# If the tree to find the parent of and the tree to search are the same, then there is no parent node, so
	# return None
	if to_search == to_find_parent_of:
		return None

	# If the tree to find the parent of is a child of the tree to search, then that is the parent, so return to_search
	if to_find_parent_of in to_search.children:
		return to_search
	else:
		# Else, iterate through each child of to_search and iteratively call the algorithm, giving a type hint for the
		# temporary variable of the for loop
		tree: Tree
		for tree in to_search.children:
			node = find_parent_of_node(tree, to_find_parent_of)
			# If the method call does not return null, then the node to find the parent of has been found either on the
			# current child of the iteration or below, so return
			if node is not None:
				return node

	return None
