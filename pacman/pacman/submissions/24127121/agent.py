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

    def predict_ghost(self, ghost_pos, pacman_pos):
        dr = ghost_pos[0] - pacman_pos[0]
        dc = ghost_pos[1] - pacman_pos[1]
        return (
            ghost_pos[0] + (1 if dr > 0 else -1 if dr < 0 else 0),
            ghost_pos[1]+ (1 if dc > 0 else -1 if dc < 0 else 0))

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
    def Heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def predict_ghost(self, ghost_pos, pacman_pos):
        dr = ghost_pos[0] - pacman_pos[0]
        dc = ghost_pos[1] - pacman_pos[1]
        return (
            ghost_pos[0] + (1 if dr > 0 else -1 if dr < 0 else 0),
            ghost_pos[1]+ (1 if dc > 0 else -1 if dc < 0 else 0))
    
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

    def predict_enemy_move(self, enemy_pos, my_pos, map_state):
        """Predict Pacman's next move (assume they move away from Ghost)."""
        best_move = Move.STAY
        best_distance = -1
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            dr, dc = move.value
            next_pos = (enemy_pos[0] + dr, enemy_pos[1] + dc)
            if not self._is_valid_position(next_pos, map_state):
                continue
            distance = self.Heuristic(next_pos, my_pos)
            if distance > best_distance:
                best_distance = distance
                best_move = move
        return (enemy_pos[0] + best_move.value[0],
                enemy_pos[1] + best_move.value[1])




    def Monte_Carlo_move(self, map_state, ghost_pos, pacman_pos, simulations=30):
        best_move = Move.STAY
        best_score = -999
        for move in[Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            dr, dc = move.value
            start = (ghost_pos[0] + dr, ghost_pos[1] + dc)
            if not self._is_valid_position(start, map_state):
                continue
            total_score = 0
            for _ in range(simulations):
                total_score += self.simulate(map_state, start, pacman_pos)
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
        predicted_enemy_pos = self.predict_enemy_move(enemy_position, my_position, map_state)
        move = self.Monte_Carlo_move(map_state, my_position, predicted_enemy_pos)
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
    def simulate(self, map_state, ghost_pos, pacman_pos, steps = 8):
        g = ghost_pos
        p = pacman_pos
        for _ in range(steps):
            moves = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]
            random.shuffle(moves)
            for m in moves:
                dr, dc = m.value
                next_pos = (g[0] + dr, g[1] + dc)
                if self._is_valid_position(next_pos, map_state):
                    g = next_pos
                    break
            # PacMan chase ghost
            best_distance = 999
            best_pos = p
            for m in moves:
                dr, dc = m.value
                next_pos = (p[0] + dr, p[1] + dc)
                if not self._is_valid_position(next_pos, map_state):
                    continue
                d = self.Heuristic(next_pos, g)
                if d < best_distance:
                    best_distance = d
                    best_pos = next_pos
            p = best_pos
        return self.Heuristic(g, p)

    def Heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
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
