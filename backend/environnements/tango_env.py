import numpy as np
import random
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class TangoEnv:
    """
    Environnement pour le puzzle Tango.

    """
    def __init__(self, grid_size=6, constraints=None, max_actions=100):

        assert grid_size % 2 == 0, "grid_size must be an even number."
        self.grid_size = grid_size
        self.symbols = ['O', 'C']
        self.constraints = constraints if constraints else {
            "equal_pairs": [],
            "diff_pairs": []
        }
        self.required_count = self.grid_size // 2  
        self.max_actions = max_actions
        self.grid = None
        self.done = False
        self.prev_grid = None  
        self.reset()

    def reset(self):
        """
        Réinitialise la grille pour un nouveau puzzle.
        La grille sera pré-remplie aléatoirement avec 5 'O' et 5 'C',
        et des contraintes aléatoires (4 égalités et 4 différences) seront générées.
        """
        self.grid = np.full((self.grid_size, self.grid_size), None, dtype=object)
        self.done = False
        self.prev_grid = None
        self.action_count = 0  

        positions = [(i, j) for i in range(self.grid_size) for j in range(self.grid_size)]
        random.shuffle(positions)

        for (r, c) in positions[:3]:
            self.grid[r][c] = 'O'
        for (r, c) in positions[7:10]:
            self.grid[r][c] = 'C'

        if not self.constraints["equal_pairs"]:
            candidate_pairs = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    candidate_pairs.append((positions[i], positions[j]))
            random.shuffle(candidate_pairs)
            self.constraints["equal_pairs"] = candidate_pairs[:4]
        if not self.constraints["diff_pairs"]:
            candidate_pairs = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    candidate_pairs.append((positions[i], positions[j]))
            random.shuffle(candidate_pairs)
            self.constraints["diff_pairs"] = candidate_pairs[:4]

        logger.debug("TangoEnv reset with random grid and constraints.")
        return self.get_state()


    def step(self, action):
        """
        Applique une action (row, col, symbol).

        :param action: Tuple (row, col, symbol).
        :return: (next_state, reward, done)
        """
        row, col, symbol = action

        if not (0 <= row < self.grid_size and 0 <= col < self.grid_size):
            raise IndexError(f"Indices {(row, col)} are out of bounds for grid size {self.grid_size}.")
        if symbol not in self.symbols:
            raise ValueError(f"Symbole invalide: {symbol}. Doit être parmi {self.symbols}.")

        self.prev_grid = self.grid.copy()

        old_value = self.grid[row][col]
        self.grid[row][col] = symbol
        logger.debug(f"Placed {symbol} at ({row}, {col}), replacing {old_value}.")

        reward = self._evaluate_action(row, col, symbol, old_value)
        self.done = self._check_if_solved()

        if not self.done and self.action_count >= self.max_actions:
            logger.debug("Maximum actions reached without solving puzzle.")
            self.done = True
            reward = -10
            return self.get_state(), reward, self.done

        self.action_count += 1

        return self.get_state(), reward, self.done

    def undo_last_action(self):
        """
        Annule la dernière action en restaurant l'état précédent de la grille.
        """
        if self.prev_grid is not None:
            self.grid = self.prev_grid.copy()
            logger.debug("Undo last action.")
        else:
            logger.debug("No previous action to undo.")

    def get_state(self):
        """
        Retourne une copie de la grille actuelle.
        """
        return self.grid.copy()

    def get_numeric_state(self):
        """
        Convertit la grille en représentation numérique : 'O' -> 0, 'C' -> 1, None -> -1.
        """
        numeric_map = {self.symbols[0]: 0, self.symbols[1]: 1, None: -1}
        numeric_grid = np.vectorize(lambda x: numeric_map[x])(self.grid)
        return numeric_grid

    def _evaluate_action(self, row, col, symbol, old_value):
        """
        Évalue la validité d'un placement et renvoie un score.

        Récompense ou pénalité en fonction de :
          - Le respect de la règle d'adjacence.
          - Le respect des contraintes '=' et 'x'.
          - La faisabilité de la distribution.
        """
        reward = 0

        if not self._check_adjacent_limit(row, col):
            reward -= 1
            logger.debug("Adjacent limit violated.")
        else:
            reward += 0.5

        if not self._check_constraints():
            reward -= 1
            logger.debug("Constraint violation detected.")
        else:
            reward += 0.5

        if not self._check_distribution_feasibility(row, col):
            reward -= 1
            logger.debug("Distribution feasibility violated.")
        else:
            reward += 0.5

        logger.debug(f"Action evaluation reward: {reward}")
        return reward

    def _check_adjacent_limit(self, row, col):
        """
        Vérifie qu'autour de (row, col), il n'y ait pas plus de deux symboles identiques consécutifs.
        """
        symbol = self.grid[row][col]
        if symbol is None:
            return True

        row_symbols = self.grid[row]
        if self._has_three_consecutive(row_symbols):
            logger.debug("Three consecutive symbols in row.")
            return False

        col_symbols = self.grid[:, col]
        if self._has_three_consecutive(col_symbols):
            logger.debug("Three consecutive symbols in column.")
            return False

        return True

    def _has_three_consecutive(self, array):
        """
        Détecte si un tableau 1D contient 3 symboles identiques consécutifs.
        """
        count = 1
        for i in range(1, len(array)):
            if array[i] is not None and array[i] == array[i - 1]:
                count += 1
                if count >= 3:
                    return True
            else:
                count = 1
        return False

    def _check_constraints(self):
        """
        Vérifie les contraintes '=' et 'x'.

        Pour chaque paire ((r1, c1), (r2, c2)) :
          - 'equal_pairs' : Les deux cellules remplies doivent être identiques.
          - 'diff_pairs' : Les deux cellules remplies doivent être différentes.
        """
        for (r1, c1), (r2, c2) in self.constraints["equal_pairs"]:
            sym1 = self.grid[r1][c1]
            sym2 = self.grid[r2][c2]
            if sym1 is not None and sym2 is not None and sym1 != sym2:
                logger.debug(f"Equal constraint violated between {(r1, c1)} and {(r2, c2)}.")
                return False

        for (r1, c1), (r2, c2) in self.constraints["diff_pairs"]:
            sym1 = self.grid[r1][c1]
            sym2 = self.grid[r2][c2]
            if sym1 is not None and sym2 is not None and sym1 == sym2:
                logger.debug(f"Difference constraint violated between {(r1, c1)} and {(r2, c2)}.")
                return False

        return True

    def _check_distribution_feasibility(self, row, col):
        """
        Vérifie si la distribution reste possible dans la ligne et la colonne modifiées,
        c'est-à-dire que le nombre de 'O' et de 'C' ne dépasse pas le nombre requis.
        """
        row_vals = self.grid[row]
        o_count = np.sum(row_vals == 'O')
        c_count = np.sum(row_vals == 'C')
        if o_count > self.required_count or c_count > self.required_count:
            logger.debug("Distribution in row not feasible.")
            return False

        col_vals = self.grid[:, col]
        o_count_col = np.sum(col_vals == 'O')
        c_count_col = np.sum(col_vals == 'C')
        if o_count_col > self.required_count or c_count_col > self.required_count:
            logger.debug("Distribution in column not feasible.")
            return False

        return True

    def _check_if_solved(self):
        """
        Vérifie si la grille est entièrement remplie et que toutes les règles sont respectées :
          1) Toutes les cellules sont remplies.
          2) Aucune ligne ni colonne ne contient 3 symboles identiques consécutifs.
          3) Chaque ligne et chaque colonne contient exactement required_count 'O' et 'C'.
          4) Les contraintes '=' et 'x' sont respectées.
        """
        if np.any(self.grid == None):
            logger.debug("Grid is not completely filled.")
            return False

        for r in range(self.grid_size):
            if self._has_three_consecutive(self.grid[r]):
                logger.debug(f"Three consecutive symbols found in row {r}.")
                return False
        for c in range(self.grid_size):
            if self._has_three_consecutive(self.grid[:, c]):
                logger.debug(f"Three consecutive symbols found in column {c}.")
                return False

        for r in range(self.grid_size):
            row_vals = self.grid[r]
            if np.sum(row_vals == 'O') != self.required_count or np.sum(row_vals == 'C') != self.required_count:
                logger.debug(f"Row {r} distribution incorrect.")
                return False

        for c in range(self.grid_size):
            col_vals = self.grid[:, c]
            if np.sum(col_vals == 'O') != self.required_count or np.sum(col_vals == 'C') != self.required_count:
                logger.debug(f"Column {c} distribution incorrect.")
                return False

        if not self._check_constraints():
            logger.debug("Constraints check failed.")
            return False

        logger.debug("Puzzle solved.")
        return True
