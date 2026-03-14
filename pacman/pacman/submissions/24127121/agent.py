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


    def A_Star(self, map_state, start, goal):
        rows, cols = map_state.shape
        pq = []
        counter = 0
        heapq.heappush(pq, (0, counter, start, []))
        visited = set()
        directions = [
            (-1, 0, Move.UP),
            (1, 0, Move.DOWN),
            (0, -1, Move.LEFT),
            (0, 1, Move.RIGHT)
            ]
        while pq:
            f,_ , pos, path = heapq.heappop(pq)
            if pos in visited:
                continue
            visited.add(pos)
            if pos == goal:
                return path
            r, c = pos
            for dr, dc, move in directions:
                nr = r + dr
                nc = c + dc
                next_pos = (nr, nc)
                if not self._is_valid_position(next_pos, map_state):
                    continue
                g = len(path) + 1
                h = self.Heuristic(next_pos, goal)
                f = g + h
                counter += 1
                heapq.heappush(
                    pq,
                    (f, counter, next_pos, path + [move]))
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
        predicted = enemy_position
        for _ in range(3):
            predict_ghost = self.predict_ghost_move(
            predicted,
            my_position,
            map_state)
        path = self.A_Star(
            map_state,
            my_position,
            predict_ghost)
        if path:
            return (path[0], 1)
        for m in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            if self._is_valid_move(my_position, m, map_state):
                return (m, 1)
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

    def predict_ghost_move(self, enemy_pos, my_pos, map_state):
        best_pos = enemy_pos
        best_distance = -1
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)]
        for dr, dc in directions:
            next_pos = (enemy_pos[0] + dr, enemy_pos[1] + dc)
            if not self._is_valid_position(next_pos, map_state):
                continue
            distance = self.Heuristic(next_pos, my_pos)
            if distance > best_distance:
                best_distance = distance
                best_pos = next_pos
        return best_pos

    def _direct_move(self, my_pos, enemy_pos):
        dr = enemy_pos[0] - my_pos[0]
        dc = enemy_pos[1] - my_pos[1]
        if dr > 0:
            return (Move.DOWN, 1)
        if dr < 0:
            return (Move.UP, 1)
        if dc > 0:
            return (Move.RIGHT, 1)
        if dc < 0:
            return (Move.LEFT, 1)
        return (Move.STAY, 1)
    
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
    Quét các nước đi hợp lệ xung quanh, dùng BFS đo khoảng cách tới Pacman 
    và chọn bước đi nào giúp cách xa Pacman nhất.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Ghost 24127474"
    
    def step(self, map_state: np.ndarray, 
             my_position: tuple, 
             enemy_position: tuple,
             step_number: int) -> Move:
        
        # Thu thập các bước đi hợp lệ không đụng tường
        valid_moves = []
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
            if self._is_valid_move(my_position, move, map_state):
                valid_moves.append(move)
                
        if not valid_moves:
            return Move.STAY

        best_move = valid_moves[0]
        max_dist = -1
        
        for move in valid_moves:
            delta_row, delta_col = move.value
            next_pos = (my_position[0] + delta_row, my_position[1] + delta_col)
            
            # Tính khoảng cách từ vị trí tiếp theo tới Pacman
            path_to_enemy = self.bfs(next_pos, enemy_position, map_state)
            dist = len(path_to_enemy) if path_to_enemy else float('inf')
            
            # Ưu tiên bước đi làm khoảng cách (dist) lớn nhất
            if dist > max_dist:
                max_dist = dist
                best_move = move
                
        return best_move
    
    def bfs(self, start, goal, map_state):
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            current_pos, path = queue.popleft()
            if current_pos == goal:
                return path
                
            for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
                if self._is_valid_move(current_pos, move, map_state):
                    delta_row, delta_col = move.value
                    next_pos = (current_pos[0] + delta_row, current_pos[1] + delta_col)
                    
                    if next_pos not in visited:
                        visited.add(next_pos)
                        queue.append((next_pos, path + [move]))
        return []

    # Helper methods từ template gốc
    def _is_valid_move(self, pos: tuple, move: Move, map_state: np.ndarray) -> bool:
        delta_row, delta_col = move.value
        new_pos = (pos[0] + delta_row, pos[1] + delta_col)
        return self._is_valid_position(new_pos, map_state)
    
    def _is_valid_position(self, pos: tuple, map_state: np.ndarray) -> bool:
        row, col = pos
        height, width = map_state.shape
        
        if row < 0 or row >= height or col < 0 or col >= width:
            return False
        
        return map_state[row, col] == 0
