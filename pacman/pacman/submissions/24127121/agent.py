"""
Template for student agent implementation.

INSTRUCTIONS:
1. Copy this file to submissions/<your_student_id>/agent.py
2. Implement the PacmanAgent and/or GhostAgent classes
3. Replace the simple logic with your search algorithm
4. Test your agent using: python arena.py --seek <your_id> --hide example_student

IMPORTANT:
- Do NOT change the class names (PacmanAgent, GhostAgent)
- Do NOT change the method signatures (step, __init__)
- Pacman step must return either a Move or a (Move, steps) tuple where
    1 <= steps <= pacman_speed (provided via kwargs)
- Ghost step must return a Move enum value
- You CAN add your own helper methods
- You CAN import additional Python standard libraries
"""

import sys
import heapq
import random
from pathlib import Path

# Add src to path to import the interface
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
from collections import deque
import numpy as np


class PacmanAgent(BasePacmanAgent):
    """
    Pacman (Seeker) Agent - Goal: Catch the Ghost
    
    Implement your search algorithm to find and catch the ghost.
    Suggested algorithms: BFS, DFS, A*, Greedy Best-First
    """
    
    def __init__(self, **kwargs):
       super().__init__(**kwargs)
       self.pacman_speed = max(1, int(kwargs.get("pacman_speed", 1)))
    # TODO: Initialize any data structures you need
    # Examples:
    # - self.path = []  # Store planned path
    # - self.visited = set()  # Track visited positions
    # - self.name = "Your Agent Name"
       self.name = "Template Pacman"
    
    def BFS(self,map_state, start, goal):
        rows, cols = map_state.shape
        queue = deque()
        queue.append((start, []))
        visited = set()
        directions = [
            (-1, 0, Move.UP),
            (1, 0, Move.DOWN),
            (0, -1, Move.LEFT),
            (0, 1, Move.RIGHT)
            ]
        while queue:
            pos, path = queue.popleft()
            if pos == goal:
                return path
            visited.add(pos)
            r, c = pos
            for dr, dc, move in directions:
                nr = r +dr
                nc = c +dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if map_state[nr][nc] == 0:
                        visited.add((nr, nc))
                        queue.append(((nr, nc), path + [move]))
        return[]

    def DFS(self, map_state, start, goal):
        rows, cols = map_state.shape
        stack = []
        stack.append((start, []))
        visited = set()
        directions = [
            (-1, 0, Move.UP),
            (1, 0, Move.DOWN),
            (0, -1, Move.LEFT),
            (0, 1, Move.RIGHT)
            ]
        while stack:
            pos, path = stack.pop()
            if pos == goal:
                return path
            if pos in visited:
                continue
            visited.add(pos)
            r, c = pos
            for dr, dc, move in directions:
                nr = r + dr
                nc = c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if map_state[nr][nc] == 0:
                        stack.append(((nr, nc), path + [move]))
        return[]

    def Heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def Greedy(self, map_state, start, goal):
        rows, cols = map_state.shape
        pq = []
        heapq.heappush(pq, (0, start, []))
        visited = set()
        directions = [
            (-1, 0, Move.UP),
            (1, 0, Move.DOWN),
            (0, -1, Move.LEFT),
            (0, 1, Move.RIGHT)]
        while pq:
            h, pos, path = heapq.heappop(pq)
            if pos == goal:
                return path
            if pos in visited:
                continue
            visited.add(pos)
            r, c = pos
            for dr, dc, move in directions:
                nr = r + dr
                nc = c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if map_state[nr][nc] == 0:
                        if(nr, nc) not in visited:
                            h = self.Heuristic((nr, nc), goal)
                            heapq.heappush(pq, (h, (nr, nc), path + [move]))
        return[]

    def A_Star(self, map_state, start, goal):
        rows, cols = map_state.shape
        pq = []
        heapq.heappush(pq, (0, start, []))
        visited = set()
        visited.add(start)
        directions = [
            (-1, 0, Move.UP),
            (1, 0, Move.DOWN),
            (0, -1, Move.LEFT),
            (0, 1, Move.RIGHT)
            ]
        while pq:
            cost, pos, path = heapq.heappop(pq)
            if pos == goal:
                return path
            r, c = pos
            for dr, dc, move in directions:
                nr = r + dr
                nc = c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if map_state[nr][nc] == 0:
                        if(nr, nc) not in visited:
                            visited.add((nr, nc))
                            g = len(path) + 1
                            h = self.Heuristic((nr, nc), goal)
                            f = g + h
                            heapq.heappush(pq, (f, (nr, nc), path + [move]))
        return[]
    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int):
        """
        Decide the next move.
        
        Args:
            map_state: 2D numpy array where 1=wall, 0=empty
            my_position: Your current (row, col)
            enemy_position: Ghost's current (row, col)
            step_number: Current step number (starts at 1)
            
        Returns:
            Move or (Move, steps): Direction to move (optionally with step count)
        """
        # TODO: Implement your search algorithm here
        path = self.A_Star(map_state, my_position, enemy_position)
        if path:
            return (path[0], 1)
        return (Move.STAY, 1)
        
        # Try to move towards ghost
        if abs(row_diff) > abs(col_diff):
            primary_move = Move.DOWN if row_diff > 0 else Move.UP
            desired_steps = abs(row_diff)
        else:
            primary_move = Move.RIGHT if col_diff > 0 else Move.LEFT
            desired_steps = abs(col_diff)

        action = self._choose_action(
            my_position,
            [primary_move],
            map_state,
            desired_steps
        )
        if action:
            return action

        # If the primary direction is blocked, try other moves
        fallback_moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
        action = self._choose_action(my_position, fallback_moves, map_state, self.pacman_speed)
        if action:
            return action

        return (Move.STAY, 1)
    
    # Helper methods (you can add more)
    
    def _choose_action(self, pos: tuple, moves, map_state: np.ndarray, desired_steps: int):
        for move in moves:
            max_steps = min(self.pacman_speed, max(1, desired_steps))
            steps = self._max_valid_steps(pos, move, map_state, max_steps)
            if steps > 0:
                return (move, steps)
        return None

    def _max_valid_steps(self, pos: tuple, move: Move, map_state: np.ndarray, max_steps: int) -> int:
        steps = 0
        current = pos
        for _ in range(max_steps):
            delta_row, delta_col = move.value
            next_pos = (current[0] + delta_row, current[1] + delta_col)
            if not self._is_valid_position(next_pos, map_state):
                break
            steps += 1
            current = next_pos
        return steps
    
    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a move from pos is valid for at least one step."""
        return self._max_valid_steps(pos, move, map_state, 1) == 1
    
    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Check if a position is valid (not a wall and within bounds)."""
        row, col = pos
        height, width = map_state.shape
        
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        
        return map_state[row, col] == 0


class GhostAgent(BaseGhostAgent):
    """
    Ghost (Hider) Agent - Goal: Avoid being caught
    
    Implement your search algorithm to evade Pacman as long as possible.
    Suggested algorithms: BFS (find furthest point), Minimax, Monte Carlo
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO: Initialize any data structures you need
        pass

    def Heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def Monte_Carlo_move(self, map_state, ghost_pos, pacman_pos, simulations=20):
        best_move = None
        best_score = -1
        for move in[Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            dr, dc = move.value
            start = (ghost_pos[0] + dr, ghost_pos[1] +dc)
            if not self._is_valid_position(start, map_state):
                continue
            total_score = 0
            for _ in range(simulations):
                pos = start
                for _ in range(5):
                    moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
                    m = random.choice(moves)
                    dr, dc = m.value
                    next_pos = (pos[0] + dr, pos[1] + dc)
                    if self._is_valid_position(next_pos, map_state):
                        pos = next_pos
                total_score += self.Heuristic(pos, pacman_pos)
            avg_score = total_score / simulations
            if avg_score > best_score:
                best_score = avg_score
                best_move = move
        return best_move

    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int) -> Move:
        """
        Decide the next move.
        
        Args:
            map_state: 2D numpy array where 1=wall, 0=empty
            my_position: Your current (row, col)
            enemy_position: Pacman's current (row, col)
            step_number: Current step number (starts at 1)
            
        Returns:
            Move: One of Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT, Move.STAY
        """
        # TODO: Implement your search algorithm here
        move = self.Monte_Carlo_move(map_state, my_position, enemy_position)
        if move and self._is_valid_move(my_position, move, map_state):
            return move
        for m in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            if self._is_valid_move(my_position, m, map_state):
                return m
        return Move.STAY
        
        # Try to move away from Pacman
        if abs(row_diff) > abs(col_diff):
            move = Move.DOWN if row_diff > 0 else Move.UP
        else:
            move = Move.RIGHT if col_diff > 0 else Move.LEFT
        
        # Check if move is valid
        if self._is_valid_move(my_position, move, map_state):
            return move
        
        # If not valid, try other moves
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            if self._is_valid_move(my_position, move, map_state):
                return move
        
        return Move.STAY
    
    # Helper methods (you can add more)
    
    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        """Check if a move from pos is valid."""
        delta_row, delta_col = move.value
        new_pos = (pos[0] + delta_row, pos[1] + delta_col)
        return self._is_valid_position(new_pos, map_state)
    
    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        """Check if a position is valid (not a wall and within bounds)."""
        row, col = pos
        height, width = map_state.shape
        
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        
        return map_state[row, col] == 0
