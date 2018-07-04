from big_ol_pile_of_manim_imports import *
from collections import OrderedDict as OrderedDict

LABELED_NODE_FACTOR = 7
UNLABELED_NODE_RADIUS = 0.1
LABELED_NODE_RADIUS = LABELED_NODE_FACTOR * UNLABELED_NODE_RADIUS
HEIGHT_RELATIVE_TO_NODE = [0, 0.23, 0.23, 0.23]

class Node(Component):
    CONFIG = {
        "fill_opacity": 0.0,
    }
    def __init__(self, point, labels=None, mobject=None,
            scale_factor=1, **kwargs):
        Component.__init__(self, point, labels=labels, mobject=mobject,
                scale_factor=scale_factor, **kwargs)

    @staticmethod
    def assert_primitive(point):
        try:
            assert type(point) == np.ndarray or type(point) == tuple
            assert len(point) == 3
        except: import ipdb; ipdb.set_trace(context=7)

    def make_key(self, point):
        return point

    def create_mobject(self, point, mobject=None, labels=None, **kwargs):
        if mobject is not None:
            return mobject.move_to(point)
        else:
            if labels is not None:
                radius = LABELED_NODE_RADIUS * self.scale_factor
            else:
                radius = UNLABELED_NODE_RADIUS
            return Circle(radius=radius, **kwargs).move_to(point)

    def __str__(self):
        return "Node(center=({}, {}))".format(*self.mobject.get_center()[:2])
    __repr__ = __str__

    def enlarge(self, **kwargs):
        if "factor" in kwargs:
            factor = kwargs["factor"]
        elif "shrink" in kwargs and kwargs["shrink"] == True:
            factor = 1./(LABELED_NODE_FACTOR * self.scale_factor)
        else:
            factor = (LABELED_NODE_FACTOR * self.scale_factor)

        new_node = self.mobject.copy().scale(factor)
        new_node.radius *= factor
        ret = ReplacementTransform(self.mobject, new_node, parent=self)
        self.mobject = new_node
        return ret

    def get_label_height(self, label, num_labels):
        return self.scale_factor * HEIGHT_RELATIVE_TO_NODE[num_labels] * \
                2 * LABELED_NODE_RADIUS / label.get_height()
    
    def get_label(self, name):
        if name in self.labels:
            return self.labels[name]
        else:
            return None

    def change_color(self, color):
        new_node = self.mobject.copy().set_color(color)
        self.mobject = new_node
        return ReplacementTransform(
            self.mobject,
            new_node,
            parent=self,
        )


    """
    scales and places labels, removes new label from self.labels
    """
    def remove_label(self, label_name):
        self.remove(self.labels[label_name])
        anims = [Uncreate(self.labels[label_name])] 
        del self.labels[label_name]
        if len(self.labels) == 1:
            # there is only one old label
            for old_label in self.labels.values():
                old_label.generate_target()
                old_label.target.move_to(self.get_center())
                anims.append(MoveToTarget(old_label))
        else:
            num_labels = len(self.labels)
            vec = rotate_vector(RIGHT, np.pi / 2)
            vec *= self.mobject.get_height() / 4.5
            for old_label in self.labels.values():
                old_label.generate_target()
                old_label.target.move_to(self.get_center() + vec)
                anims.append(MoveToTarget(old_label))
                vec = rotate_vector(vec, 2 * np.pi / num_labels)
        return anims

    """
    scales and places labels, saves new label to self.labels
    """
    def set_label(self, name, label, animate=True, **kwargs):
        kwargs["animate"] = animate
        return self.set_labels((name, label), **kwargs)

    def set_labels(self, *labels, **kwargs):
        if not labels:
            return

        # copy
        new_labels = OrderedDict()
        for name in self.labels.keys():
            new_labels[name] = self.labels[name].copy()
        for name, label in labels:
            new_labels[name] = label
    
        # move
        if len(new_labels) != len(self.labels):
            # rearrange labels
            if len(new_labels) == 1:
                label.move_to(self.get_center())
            else:
                vec = rotate_vector(RIGHT, np.pi / 2)
                vec *= LABELED_NODE_RADIUS / 2.4 * self.scale_factor
                for label in new_labels.values():
                    label.move_to(self.get_center() + vec)
                    vec = rotate_vector(vec, 2 * np.pi / len(new_labels))
        else:
            assert(new_labels.keys() == self.labels.keys())
            for name in new_labels:
                new_labels[name].move_to(self.labels[name].get_center())

        # scale
        for label in new_labels.values():
            if type(label) == Arrow: continue # TODO: lol
            new_height = self.get_label_height(label, len(new_labels))
            label.scale(new_height)

        # animate / create
        anims = []
        for name in new_labels.keys():
            if "animate" not in kwargs or kwargs["animate"]:
                if name in self.labels:
                    anims.extend([ReplacementTransform(self.labels[name],
                                                       new_labels[name],
                                                       parent=self)])
                else:
                    anims.extend([ShowCreation(new_labels[name])])
                    self.add(new_labels[name])
            else:
                if name not in self.labels:
                    self.add(new_labels[name])
        self.labels = new_labels
        return anims
