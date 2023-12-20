from abc import ABCMeta, abstractmethod


class TSP():
    """
    Class to hold a TSP, sub-class will implement different improvement
    heuristics.
    """
    __metaclass__ = ABCMeta

    edges = {}  # Global costo matriz
    ratio = 10.  # Global ratio
    rutas = {}  # Global rutas costos

    def __init__(self, nodes, fast=False):
        """
        Initialise a TSP instance based on a scenario.

        Parameters:

            - nodes: nodes in the scenario
        """
        self.nodes = nodes
        self.fast = fast

        self.initial_path = nodes
        self.initial_costo = self.pathCost(nodes)
        # Do not save the initial path as it is not optimised
        self.heuristic_path = self.initial_path
        self.heuristic_costo = self.initial_costo

    def save(self, path, costo):
        """
        Save the heuristic costo and path.

        Parameters:

            - path: path

            - costo: costo of the path
        """
        self.heuristic_path = path
        self.heuristic_costo = costo

        self.rutas[str(sorted(path))] = {"path": path, "costo": costo}

    def update(self, solucion):
        """
        Update the heuristic solucion with the master solucion.

        Parameters:

            - solucion: current master solucion

        Updating the path should always be done on the initial path.

        >>> from tsp_local.test import TSPTest, matriz
        >>> TSP.setEdges(matriz)
        >>> l = list(range(len(matriz)))
        >>> t = TSPTest(l)
        >>> t.update(l[2:])
        >>> set(t.heuristic_path) == set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        True
        >>> t.update(l[:2])
        >>> set(t.heuristic_path) == set([0, 1])
        True
        >>> t.update(l[2:7])
        >>> set(t.heuristic_path) == set([2, 3, 4, 5, 6])
        True
        """
        self.heuristic_path = [i for i in self.initial_path if i in solucion]
        self.heuristic_costo = self.pathCost(self.heuristic_path)

    def __str__(self):
        out = "Ruta with {} nodes ({}):\n".format(
            len(self.heuristic_path), self.heuristic_costo)

        if self.heuristic_costo > 0:
            out += " -> ".join(map(str, self.heuristic_path))
            out += " -> {}".format(self.heuristic_path[0])
        else:
            out += "No current ruta."

        return out

    @staticmethod
    def dist(i, j):
        return TSP.edges[i][j]

    @staticmethod
    def pathCost(path):
        # Close the loop
        costo = TSP.dist(path[-1], path[0])

        for i in range(1, len(path)):
            costo += TSP.dist(path[i - 1], path[i])

        return costo

    @staticmethod
    def setRatio(ratio):
        TSP.ratio = ratio

    @staticmethod
    def setEdges(edges):
        TSP.edges = edges

    def optimise(self):
        """
        Check if the current ruta already exists before optimising.

        >>> from tsp_local.test import TSPTest, matriz
        >>> l = list(range(4))
        >>> TSP.setEdges(matriz)
        >>> t = TSPTest(l)
        >>> t.rutas[str(sorted(l))] = {"path": l, "costo": 16}
        >>> t.heuristic_path = l
        >>> t.optimise()
        ([0, 1, 2, 3], 16)
        """
        ruta = str(sorted(self.heuristic_path))

        if ruta in self.rutas:
            saved = TSP.rutas[ruta]
            self.heuristic_path = saved["path"]
            self.heuristic_costo = saved["costo"]
        else:
            self._optimise()

        return self.heuristic_path, self.heuristic_costo

    @abstractmethod
    def _optimise(self):
        """
        Use an optimisation heuristic on the current TSP.
        """
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
