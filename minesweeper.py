import itertools as iter
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
                        
        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if the number of cells is equal to the count, all are mines.
        if len(self.cells) > 0 and len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if count = 0, all are safe
        if len(self.cells) > 0 and self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        try:
            # remove cell from set and decrease count of sentence by 1
            self.cells.remove(cell)
            self.count -= 1
        except KeyError:
            # remove() method will raise exeption if cell not in sentence
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        try:
            # remove cell from set. count of sentence is unchanged.
            self.cells.remove(cell)
        except KeyError:
            # remove() method will raise exeption if cell not in sentence
            pass


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        # remove this cell from all sentences, and reduce the 
        # affected sentences' counts by 1
        for sentence in self.knowledge:
            sentence.mark_mine(cell) 

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        # remove this cell from all sentences (sentence counts are unchanged)
        for sentence in self.knowledge:
            sentence.mark_safe(cell) 

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Gather new knowledge from revealed cell
        nearby_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # We know the cell itself is safe, so don't add it to the sentence
                if (i, j) == cell:
                    continue
                # Only include cells that we don't already know to be safe
                if 0 <= i < self.height and 0 <= j < self.width and (i, j) not in self.safes:
                    nearby_cells.add((i, j))
        new_knowledge = Sentence(nearby_cells, count)

        # Update knowledge base if we find any new mines/safes
        if len(new_knowledge.cells) > 0:
            if new_knowledge.known_mines():
                for cell in new_knowledge.known_mines():
                    self.mark_mine(cell)
            if new_knowledge.known_safes():
                for cell in new_knowledge.known_safes():
                    self.mark_safe(cell)
        
        # Add new knowledge to knowledge base, then analyse all knowledge 
        # to see if new inferences can be made.
        self.knowledge.append(new_knowledge)
        if len(self.knowledge) > 0:
            self.knowledge.sort(key = lambda sentence : len(sentence.cells))
            done = []
            changes_made = False
            while True:
                if len(self.knowledge) > 1:
                    # remove the first (ie, smallest) sentence from knowledge
                    fact = self.knowledge.pop(0)
                    if len(fact.cells) == 0:
                        # discard empty sentences (don't add to 'done' list)
                        continue
                    else:
                        for sentence in self.knowledge:
                            # if fact is a subset of this sentence
                            if fact.cells <= sentence.cells:
                                # recalculate the logic of the sentence
                                sentence.cells -= fact.cells
                                sentence.count -= fact.count
                                changes_made = True
                        done.append(fact)
                        continue
                else:
                    if len(self.knowledge) == 1:
                        done.append(self.knowledge[0])
                    else:
                        # We have an empty knowledge base
                        break
                if not changes_made:
                    self.knowledge = done
                    break
                # Changes made to knowledge base. Do another analysis.
                self.knowledge = done
                done = []
                changes_made = False
                            
        # Go through knowledge and flag any newly discovered mines or safes
        for sentence in self.knowledge:
            if sentence.known_mines():
                for mine in sentence.cells:
                    self.mines.add(mine)
            if sentence.known_safes():
                for safe in sentence.cells:
                    self.safes.add(safe)
        

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        safe_moves = self.safes - self.moves_made
        if len(safe_moves) > 0:
            choice = random.choice([move for move in safe_moves])
            return choice
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set()
        for i, j in iter.product(range(self.height), range(self.width)):
            all_cells.add((i, j))
        remaining = all_cells - self.moves_made - self.mines
        if remaining:
            choice = random.choice([move for move in remaining])
            return choice
        return None
