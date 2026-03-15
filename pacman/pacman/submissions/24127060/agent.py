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
from pathlib import Path

# Add src to path to import the interface
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
from environment import Move
import numpy as np
import collections
import math
import heapq

class PacmanAgent(BasePacmanAgent):
    """
    Pacman (Seeker) Agent - Goal: Catch the Ghost
    
    Implement your search algorithm to find and catch the ghost.
    Suggested algorithms: BFS, DFS, A*, Greedy Best-First
    """
    
    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.pacman_speed = 2
    # TODO: Initialize any data structures you need
    # Examples:
    # - self.path = []  # Store planned path
    # - self.visited = set()  # Track visited positions
    # - self.name = "Your Agent Name"
            self.name = "A* Pacman"
    
    def heuristic(self, a, b):
        """Sử dụng khoảng cách Manhattan làm hàm Heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar_search(self, start, goal, map_state):
        """Tìm đường đi ngắn nhất bằng A*."""
        # Priority Queue lưu: (f_score, current_pos, path)
        frontier = []
        heapq.heappush(frontier, (0, start, []))
        
        # g_score: chi phí thực tế từ điểm bắt đầu
        g_score = {start: 0}
        visited = set()

        while frontier:
            f, current, path = heapq.heappop(frontier)

            if current == goal:
                return path

            if current in visited:
                continue
            visited.add(current)

            for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
                dr, dc = move.value
                neighbor = (current[0] + dr, current[1] + dc)

                if self._is_valid_position(neighbor, map_state):
                    new_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or new_g_score < g_score[neighbor]:
                        g_score[neighbor] = new_g_score
                        f_score = new_g_score + self.heuristic(neighbor, goal)
                        heapq.heappush(frontier, (f_score, neighbor, path + [move]))
        return []
    
    def step(self, map_state, my_position, enemy_position, step_number):
        path = self.astar_search(my_position, enemy_position, map_state)
        
        if not path:
            return Move.STAY

        # Tính khoảng cách Manhattan hiện tại
        dist = self.heuristic(my_position, enemy_position)
        first_move = path[0]

        # SỬA TẠI ĐÂY: Nếu khoảng cách <= 2, ta nên đi 1 bước duy nhất 
        # để tăng tỷ lệ va chạm chính xác, tránh việc nhảy quá đà (overshooting)
        if dist <= 2:
            return (first_move, 1)

        # Logic di chuyển 2 bước cho các trường hợp ở xa
        if len(path) >= 2:
            second_move = path[1]
            if first_move == second_move:
                pos_1 = (my_position[0] + first_move.value[0], my_position[1] + first_move.value[1])
                pos_2 = (pos_1[0] + second_move.value[0], pos_1[1] + second_move.value[1])
                
                if self._is_valid_position(pos_2, map_state):
                    return (first_move, 2)

        return (first_move, 1)
    
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
    
    def _manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


class GhostAgent(BaseGhostAgent):
    """
    Ghost (Hider) Agent - Goal: Avoid being caught
    
    Implement your search algorithm to evade Pacman as long as possible.
    Suggested algorithms: BFS (find furthest point), Minimax, Monte Carlo
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Minimax Ghost"
        self.search_depth = 3
        # TODO: Initialize any data structures you need
        pass
    
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
        best_move = Move.STAY
        max_val = -math.inf

        # Ghost chọn nước đi dẫn đến kết quả Minimax tốt nhất
        for next_pos, move in self._get_neighbors(my_position, map_state):
            val = self.minimax(next_pos, enemy_position, self.search_depth, False, map_state)
            if val > max_val:
                max_val = val
                best_move = move
        
        return best_move
    
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
    
    def _get_neighbors(self, pos, map_state):
        neighbors = []
        for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT, Move.STAY]:
            dr, dc = move.value
            next_pos = (pos[0] + dr, pos[1] + dc)
            if 0 <= next_pos[0] < map_state.shape[0] and \
               0 <= next_pos[1] < map_state.shape[1] and \
               map_state[next_pos] == 0:
                neighbors.append((next_pos, move))
        return neighbors

    def evaluation_function(self, ghost_pos, pacman_pos):
        # Ghost muốn tối đa hóa khoảng cách Manhattan 
        return abs(ghost_pos[0] - pacman_pos[0]) + abs(ghost_pos[1] - pacman_pos[1])

    def minimax(self, ghost_pos, pacman_pos, depth, is_ghost_turn, map_state):
        # Trạng thái kết thúc: đạt độ sâu tối đa hoặc bị bắt 
        if depth == 0 or ghost_pos == pacman_pos:
            return self.evaluation_function(ghost_pos, pacman_pos)

        if is_ghost_turn:
            max_eval = -math.inf
            for next_ghost, _ in self._get_neighbors(ghost_pos, map_state):
                eval = self.minimax(next_ghost, pacman_pos, depth - 1, False, map_state)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = math.inf
            for next_pacman, _ in self._get_neighbors(pacman_pos, map_state):
                # Lưu ý: Pacman có thể đi 2 bước nếu đi thẳng 
                # Ở đây ta giả định Pacman đi 1 bước để đơn giản hóa tính toán
                eval = self.minimax(ghost_pos, next_pacman, depth - 1, True, map_state)
                min_eval = min(min_eval, eval)
            return min_eval