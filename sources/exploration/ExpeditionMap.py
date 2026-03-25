import typing
from random import randint

from lib.utils import use_font

from .Node import Node


class ExpeditionMap:
    """
    Gère la carte d'exploration , avec les nodes et leurs connexions.
    """

    def __init__(self, seed=None):
        self.seed = seed or randint(0, 10000)
        self.root_node = Node(node_id=0, parent=None, depth=0, seed=self.seed)
        self.root_node.is_discovered = True
        self.root_node.is_visible = True
        self.all_nodes = [self.root_node]
        self.current = self.root_node

    def get_visible_nodes(self):
        visible = []

        def traverse(node):
            if node.is_visible:
                visible.append(node)
            for child in node.children:
                traverse(child)

        traverse(self.root_node)
        return visible

    def clear(self, node):
        if node.is_cleared:
            return
        node.is_cleared = True
        node.generate_child()
        for child in node.children:
            child.is_visible = True
            self.all_nodes.append(child)

    def get_node_at_pos(self, x, y, click_radius=30) -> typing.Optional[Node]:
        for node in self.get_visible_nodes():
            if not node.is_discovered:
                continue
            node_x, node_y = node.position
            distance = ((x - node_x) ** 2 + (y - node_y) ** 2) ** 0.5

            if distance <= click_radius:
                return node
        return None

    def node_is_accessible(self, node):
        if not node.is_discovered:
            return False
        if node.parent is None:
            return True
        return node.parent.is_cleared

    def draw(self, screen, cam_x, cam_y):
        visible_nodes = self.get_visible_nodes()

        for node in visible_nodes:
            node.draw_links(screen, cam_x, cam_y)
        for node in visible_nodes:
            node.draw(
                screen, cam_x, cam_y
            )  # Deux boucles pour que les nodes soient au-dessus des connections
        self.draw_info(screen, visible_nodes)

    def draw_info(self, screen, nodes):
        font = use_font(24)
        cur_x, cur_y = self.current.position
        info_y = 20
        text = [
            f"Current Node: {self.current.node_id}",
            f"Difficulty:{self.current.difficulty}",
            f"Status: {'Conquered' if self.current.is_cleared else 'Enemy territory'}",
            f"Donne acces a {len(self.current.children)} nodes",
        ]
        for i, line in enumerate(text):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, info_y + i * 25))

    def serialize(self):
        """
        Sérialise l'état de la carte (noeuds, seed, current).
        """
        nodes = []
        for node in self.all_nodes:
            nodes.append(
                {
                    "node_id": node.node_id,
                    "parent_id": node.parent.node_id if node.parent else None,
                    "depth": node.depth,
                    "is_cleared": node.is_cleared,
                    "is_discovered": node.is_discovered,
                    "is_visible": node.is_visible,
                    "seed": node.seed,
                    "position": node.position,
                }
            )
        return {
            "seed": self.seed,
            "current_node_id": self.current.node_id if self.current else None,
            "all_nodes": nodes,
        }

    def restore(self, data: dict):
        """
        Reconstruit la carte à partir des données sauvegardées.
        """
        self.seed = data.get("seed", self.seed)
        all_nodes_data = data.get("all_nodes", [])
        node_map = {}
        self.all_nodes = []

        # Créer les noeuds sans parents
        for nd in all_nodes_data:
            node = Node(
                node_id=nd["node_id"],
                parent=None,
                depth=nd.get("depth", 0),
                seed=nd.get("seed"),
            )
            node.is_cleared = nd.get("is_cleared", False)
            node.is_discovered = nd.get("is_discovered", False)
            node.is_visible = nd.get("is_visible", False)
            node.position = tuple(nd.get("position", node.position))
            node.children = []
            node.num_children = node.child_count()
            node_map[node.node_id] = node
            self.all_nodes.append(node)

        # Assigner parents et enfants
        for nd in all_nodes_data:
            node = node_map.get(nd["node_id"])
            parent_id = nd.get("parent_id")
            if parent_id is not None:
                parent = node_map.get(parent_id)
                if parent:
                    node.parent = parent
                    parent.children.append(node)

        self.root_node = next((n for n in self.all_nodes if n.parent is None), None)
        if self.root_node is None and self.all_nodes:
            self.root_node = self.all_nodes[0]
        elif self.root_node is None:
            self.root_node = Node(node_id=0, parent=None, depth=0, seed=self.seed)
            self.root_node.is_discovered = True
            self.root_node.is_visible = True
            self.all_nodes.append(self.root_node)

        self.current = node_map.get(data.get("current_node_id"), self.root_node)
