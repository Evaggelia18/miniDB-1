'''
https://en.wikipedia.org/wiki/B%2B_tree
'''
import math


class Node:
    '''
    Node abstraction. Represents a single bucket
    '''

    def __init__(self, b, values=[], ptrs=[], \
                 left_sibling=None, right_sibling=None, parent=None, is_leaf=False):
        self.b = b  # branching factor
        self.values = values  # Values (the data from the pk column)
        self.ptrs = ptrs  # ptrs (the indexes of each datapoint or the index of another bucket)
        self.left_sibling = left_sibling  # the index of a buckets left sibling
        self.right_sibling = right_sibling  # the index of a buckets right sibling
        self.parent = parent  # the index of a buckets parent
        self.is_leaf = is_leaf  # a boolean value signaling whether the node is a leaf or not

    def find(self, value, return_ops=False):
        '''
        Returns the index of the next node to search for a value if the node is not a leaf (a ptrs of the available ones).
        If it is a leaf (we have found the appropriate node), it returns nothing.

        value: the value that we are searching for
        return_ops: set to True if you want to use the number of operations (for benchmarking)
        '''
        ops = 0  # number of operations (<>= etc). Used for benchmarking
        if self.is_leaf:  #
            return

        # for each value in the node, if the user supplied value is smaller, return the btrees value index
        # else (no value in the node is larger) return the last ptr
        for index, existing_val in enumerate(self.values):
            ops += 1
            if value < existing_val:
                if return_ops:
                    return self.ptrs[index], ops
                else:
                    return self.ptrs[index]

        if return_ops:
            return self.ptrs[-1], ops
        else:
            return self.ptrs[-1]

    def insert(self, value, ptr, ptr1=None):
        '''
        Insert the value and its ptr/s to the appropriate place (node wise).
        User can input two ptrs to insert to a non leaf node.

        value: the value that we are inserting to the node
        ptr: the ptr of the inserted value (its index for example)
        ptr1: the 2nd ptr (in case the user wants to insert into a nonleaf node for ex)

        '''
        # for each value in the node, if the user supplied value is smaller, insert the value and its ptr into that position
        # if a second ptr is provided, insert it right next to the 1st ptr
        # else (no value in the node is larger) append value and ptr/s to the back of the list.

        for index, existing_val in enumerate(self.values):
            if value < existing_val:

                self.values.insert(index, value)
                self.ptrs.insert(index + 1, ptr)

                if ptr1:
                    self.ptrs.insert(index + 1, ptr1)
                return
        self.values.append(value)
        self.ptrs.append(ptr)
        if ptr1:
            self.ptrs.append(ptr1)

    def show(self):
        '''
        print the node's value and important info
        '''
        print('Values', self.values)
        print('ptrs', self.ptrs)
        print('Parent', self.parent)
        print('LS', self.left_sibling)
        print('RS', self.right_sibling)


class Btree:
    def __init__(self, b):
        '''
        The tree abstraction.
        '''
        self.b = b  # branching factor
        self.nodes = []  # list of nodes. Every new node is appended here
        self.root = None  # the index of the root node

    def insert(self, value, ptr, rptr=None):
        '''
        Insert the value and its ptr/s to the appropriate node (node-level insertion is covered by the node object).
        User can input two ptrs to insert to a non leaf node.
        '''
        # if the tree is empty, add the first node and set the root index to 0 (the only node's index)
        if self.root is None:
            self.nodes.append(Node(self.b, is_leaf=True))
            self.root = 0

        # find the index of the node that the value and its ptr/s should be inserted to (_search)
        index = self._search(value)
        # insert to it
        self.nodes[index].insert(value, ptr)
        # if the node has more elements than b-1, split the node
        if len(self.nodes[index].values) == self.b:
            self.split(index)

    def _search(self, value, return_ops=False):
        '''
        Returns the index of the node that the given value exist or should exist in.

        value: the value that we are searching for
        return_ops: set to True if you want to use the number of operations (for benchmarking)
        '''
        ops = 0  # number of operations (<>= etc). Used for benchmarking

        # start with the root node
        node = self.nodes[self.root]
        # while the node that we are searching in is not a leaf
        # keep searching
        while not node.is_leaf:
            idx, ops1 = node.find(value, return_ops=True)
            node = self.nodes[idx]
            ops += ops1

        # finally return the index of the appropriate node (and the ops if you want to)
        if return_ops:
            return self.nodes.index(node), ops
        else:
            return self.nodes.index(node)

    def split(self, node_id):
        '''
        Split the node with index=node_id
        '''
        # fetch the node to be split
        node = self.nodes[node_id]
        # the value that will be propagated to the parent is the middle one.
        new_parent_value = node.values[len(node.values) // 2]
        if node.is_leaf:
            # if the node is a leaf, the parent value should be a part of the new node (right)
            # Important: in a b+tree, every value should appear in a leaf
            right_values = node.values[len(node.values) // 2:]
            right_ptrs = node.ptrs[len(node.ptrs) // 2:]

            # create the new node with the right half of the old nodes values and ptrs (including the middle ones)
            right = Node(self.b, right_values, right_ptrs, \
                         left_sibling=node_id, right_sibling=node.right_sibling, parent=node.parent,
                         is_leaf=node.is_leaf)
            # since the new node (right) will be the next one to be appended to the nodes list
            # its index will be equal to the length of the nodes list.
            # Thus we set the old nodes (now left) right sibling to the right nodes future index (len of nodes)
            if node.right_sibling is not None:
                self.nodes[node.right_sibling].left_sibling = len(self.nodes)
            node.right_sibling = len(self.nodes)
        else:
            # if the node is not a leaf, the parent value shoudl NOT be part of the new node
            right_values = node.values[len(node.values) // 2 + 1:]
            if self.b % 2 == 1:
                right_ptrs = node.ptrs[len(node.ptrs) // 2:]
            else:
                right_ptrs = node.ptrs[len(node.ptrs) // 2 + 1:]

            # if nonleafs should be connected change the following two lines and add siblings
            right = Node(self.b, right_values, right_ptrs, \
                         parent=node.parent, is_leaf=node.is_leaf)
            # make sure that a non leaf node doesnt have a parent
            node.right_sibling = None
            # the right node's kids should have him as a parent (if not all nodes will have left as parent)
            for ptr in right_ptrs:
                self.nodes[ptr].parent = len(self.nodes)

        # old node (left) keeps only the first half of the values/ptrs
        node.values = node.values[:len(node.values) // 2]
        if self.b % 2 == 1:
            node.ptrs = node.ptrs[:len(node.ptrs) // 2]
        else:
            node.ptrs = node.ptrs[:len(node.ptrs) // 2 + 1]

        # append the new node (right) to the nodes list
        self.nodes.append(right)

        # If the new nodes have no parents (a new level needs to be added
        if node.parent is None:
            # its the root that is split
            # new root contains the parent value and ptrs to the two recently split nodes
            parent = Node(self.b, [new_parent_value], [node_id, len(self.nodes) - 1] \
                          , parent=node.parent, is_leaf=False)

            # set root, and parent of split celss to the index of the new root node (len of nodes-1)
            self.nodes.append(parent)
            self.root = len(self.nodes) - 1
            node.parent = len(self.nodes) - 1
            right.parent = len(self.nodes) - 1
        else:
            # insert the parent value to the parent

            self.nodes[node.parent].insert(new_parent_value, len(self.nodes) - 1)
            # check whether the parent needs to be split
            if len(self.nodes[node.parent].values) == self.b:
                self.split(node.parent)

    # Delete a node
    def delete(self, value, ptr):
        node_ = self.nodes[self._search(value)]

        temp = 0
        for i, item in enumerate(node_.values):
            if item == value:
                temp = 1

                if ptr == node_.ptrs[i]:
                    if len(node_.ptrs) > 1:
                        node_.ptrs.pop(node_.ptrs.index(ptr))
                    elif node_ == self.root:
                        node_.values.pop(i)
                        node_.ptrs.pop(i)
                    else:
                        node_.ptrs.pop(node_.ptrs.index(ptr))
                        del node_.ptrs[i]
                        node_.values.pop(node_.values.index(value))
                        self.deleteEntry(node_, value, ptr)
                else:
                    print("Value not in ptr")
                    return
        if temp == 0:
            print("Value not in Tree")
            return

    # Delete an entry
    def deleteEntry(self, node_, value, ptr):

        if not node_.check_leaf:
            for i, item in enumerate(node_.ptrs):
                if item == ptr:
                    node_.ptrs.pop(i)
                    break
            for i, item in enumerate(node_.values):
                if item == value:
                    node_.values.pop(i)
                    break

        if self.root == node_ and len(node_.ptrs) == 1:
            self.root = node_.ptrs[0]
            node_.ptrs[0].parent = None
            del node_
            return
        elif (len(node_.ptrs) < int(math.ceil(node_.order / 2)) and node_.check_leaf == False) or (
                len(node_.values) < int(math.ceil((node_.order - 1) / 2)) and node_.check_leaf == True):

            is_predecessor = 0
            parentNode = node_.parent
            PrevNode = -1
            NextNode = -1
            PrevK = -1
            PostK = -1
            for i, item in enumerate(parentNode.ptrs):

                if item == node_:
                    if i > 0:
                        PrevNode = parentNode.ptrs[i - 1]
                        PrevK = parentNode.values[i - 1]

                    if i < len(parentNode.ptrs) - 1:
                        NextNode = parentNode.ptrs[i + 1]
                        PostK = parentNode.values[i]

            if PrevNode == -1:
                ndash = NextNode
                value_ = PostK
            elif NextNode == -1:
                is_predecessor = 1
                ndash = PrevNode
                value_ = PrevK
            else:
                if len(node_.values) + len(NextNode.values) < node_.order:
                    ndash = NextNode
                    value_ = PostK
                else:
                    is_predecessor = 1
                    ndash = PrevNode
                    value_ = PrevK

            if len(node_.values) + len(ndash.values) < node_.order:
                if is_predecessor == 0:
                    node_, ndash = ndash, node_
                ndash.ptrs += node_.ptrs
                if not node_.check_leaf:
                    ndash.values.append(value_)
                else:
                    ndash.nextptr = node_.nextptr
                ndash.values += node_.values

                if not ndash.check_leaf:
                    for j in ndash.ptrs:
                        j.parent = ndash

                self.deleteEntry(node_.parent, value_, node_)
                del node_
            else:
                if is_predecessor == 1:
                    if not node_.check_leaf:
                        ndashpm = ndash.ptrs.pop(-1)
                        ndashkm_1 = ndash.values.pop(-1)
                        node_.ptrs = [ndashpm] + node_.ptrs
                        node_.values = [value_] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                p.values[i] = ndashkm_1
                                break
                    else:
                        ndashpm = ndash.ptrs.pop(-1)
                        ndashkm = ndash.values.pop(-1)
                        node_.ptrs = [ndashpm] + node_.ptrs
                        node_.values = [ndashkm] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(p.values):
                            if item == value_:
                                parentNode.values[i] = ndashkm
                                break
                else:
                    if not node_.check_leaf:
                        ndashp0 = ndash.ptrs.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.ptrs = node_.ptrs + [ndashp0]
                        node_.values = node_.values + [value_]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashk0
                                break
                    else:
                        ndashp0 = ndash.ptrs.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.ptrs = node_.ptrs + [ndashp0]
                        node_.values = node_.values + [ndashk0]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndash.values[0]
                                break

                if not ndash.check_leaf:
                    for j in ndash.ptrs:
                        j.parent = ndash
                if not node_.check_leaf:
                    for j in node_.ptrs:
                        j.parent = node_
                if not parentNode.check_leaf:
                    for j in parentNode.ptrs:
                        j.parent = parentNode
    def show(self):
        '''
        Show important info for each node (sort the by level - root first, then left to right)
        '''
        nds = []
        nds.append(self.root)
        for ptr in nds:
            if self.nodes[ptr].is_leaf:
                continue
            nds.extend(self.nodes[ptr].ptrs)

        for ptr in nds:
            print(f'## {ptr} ##')
            self.nodes[ptr].show()
            print('----')

    def plot(self):
        ## arrange the nodes top to bottom left to right
        nds = []
        nds.append(self.root)
        for ptr in nds:
            if self.nodes[ptr].is_leaf:
                continue
            nds.extend(self.nodes[ptr].ptrs)

        # add each node and each link
        g = 'digraph G{\nforcelabels=true;\n'

        for i in nds:
            node = self.nodes[i]
            g += f'{i} [label="{node.values}"]\n'
            if node.is_leaf:
                continue
                # if node.left_sibling is not None:
                #     g+=f'"{node.values}"->"{self.nodes[node.left_sibling].values}" [color="blue" constraint=false];\n'
                # if node.right_sibling is not None:
                #     g+=f'"{node.values}"->"{self.nodes[node.right_sibling].values}" [color="green" constraint=false];\n'
                #
                # g+=f'"{node.values}"->"{self.nodes[node.parent].values}" [color="red" constraint=false];\n'
            else:
                for child in node.ptrs:
                    g += f'{child} [label="{self.nodes[child].values}"]\n'
                    g += f'{i}->{child};\n'
        g += "}"

        try:
            from graphviz import Source
            src = Source(g)
            src.render('bplustree', view=True)
        except ImportError:
            print('"graphviz" package not found. Writing to graph.gv.')
            with open('graph.gv', 'w') as f:
                f.write(g)

    def find(self, operator, value):
        '''
        Return ptrs of elements where btree_value"operator"value.
        Important, the user supplied "value" is the right value of the operation. That is why the operation are reversed below.
        The left value of the op is the btree value.
        '''
        results = []
        # find the index of the node that the element should exist in
        leaf_idx, ops = self._search(value, True)
        target_node = self.nodes[leaf_idx]

        if operator == '==':
            # if the element exist, append to list, else pass and return
            try:
                results.append(target_node.ptrs[target_node.values.index(value)])
                # print('Found')
            except:
                # print('Not found')
                pass

        # for all other ops, the code is the same, only the operations themselves and the sibling indexes change
        # for > and >= (btree value is >/>= of user supplied value), we return all the right siblings (all values are larger than current cell)
        # for < and <= (btree value is </<= of user supplied value), we return all the left siblings (all values are smaller than current cell)

        if operator == '>':
            for idx, node_value in enumerate(target_node.values):
                ops += 1
                if node_value > value:
                    results.append(target_node.ptrs[idx])
            while target_node.right_sibling is not None:
                target_node = self.nodes[target_node.right_sibling]
                results.extend(target_node.ptrs)

        if operator == '>=':
            for idx, node_value in enumerate(target_node.values):
                ops += 1
                if node_value >= value:
                    results.append(target_node.ptrs[idx])
            while target_node.right_sibling is not None:
                target_node = self.nodes[target_node.right_sibling]
                results.extend(target_node.ptrs)

        if operator == '<':
            for idx, node_value in enumerate(target_node.values):
                ops += 1
                if node_value < value:
                    results.append(target_node.ptrs[idx])
            while target_node.left_sibling is not None:
                target_node = self.nodes[target_node.left_sibling]
                results.extend(target_node.ptrs)

        if operator == '<=':
            for idx, node_value in enumerate(target_node.values):
                ops += 1
                if node_value <= value:
                    results.append(target_node.ptrs[idx])
            while target_node.left_sibling is not None:
                target_node = self.nodes[target_node.left_sibling]
                results.extend(target_node.ptrs)

        # print the number of operations (usefull for benchamrking)
        print(f'With BTree -> {ops} comparison operations')
        return results
