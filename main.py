from itertools import product
import pygame
import numpy as np
from random import choice, randint, random
from collections import deque
import os
from math import sqrt

pygame.init()
direction = True

# Всякие параметры, их можно изменить на свой вкус
REC = WIDTH, HEIGHT = 1280, 700
TILE = 100
cols, rows = WIDTH // TILE, HEIGHT // TILE
player_size = TILE - 4
SIMPLE_DISTANCE = False
SHOW_FLAG = True
SHOW_PATH_LINE = True
CHAOS_LABIRINT = True

# Что как сохранять
SAVE_LABIRINT_GENERATING = False
SAVE_KUKUSIK_PATH = False

win = pygame.display.set_mode(REC)
clock = pygame.time.Clock()
kukusik_right = pygame.transform.smoothscale(pygame.image.load("Kukusik.png"), (TILE * 0.7, TILE * 0.7))
kukusik_left = pygame.transform.flip(kukusik_right, True, False)

class Cell:
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
		self.walls = {"top": True, "right": True, "bottom": True, "left": True}
		self.visited = False
	
	def draw_current_cell(self):
		x, y = self.x * TILE, self.y * TILE
		pygame.draw.rect(win, pygame.Color("saddlebrown"), (x + 2, y + 2, TILE - 2, TILE - 2))
	
	def draw(self):
		x, y = self.x * TILE, self.y * TILE
		if self.visited:
			pygame.draw.rect(win, pygame.Color((255, 255, 255)), (x, y, TILE, TILE))
		
		if self.walls["top"]:
			pygame.draw.line(win, pygame.Color("blue"), (x, y), (x + TILE, y), TILE // 10)
		if self.walls["right"]:
			pygame.draw.line(win, pygame.Color("blue"), (x + TILE, y), (x + TILE, y + TILE), TILE // 10)
		if self.walls["bottom"]:
			pygame.draw.line(win, pygame.Color("blue"), (x + TILE, y + TILE), (x, y + TILE), TILE // 10)
		if self.walls["left"]:
			pygame.draw.line(win, pygame.Color("blue"), (x, y + TILE), (x, y), TILE // 10)
	
	def check_cell(self, x: int, y: int):
		find_index = lambda x, y: x + y * cols
		if x < 0 or x > cols - 1 or y < 0 or y > rows -1:
			return False
		return grid_cells[find_index(x, y)]
	
	def check_neighbors(self):
		neighbors = []
		top = self.check_cell(self.x, self.y - 1)
		right = self.check_cell(self.x + 1, self.y)
		bottom = self.check_cell(self.x, self.y + 1)
		left = self.check_cell(self.x - 1, self.y)
		if top and not top.visited:
			neighbors.append(top)
		if right and not right.visited:
			neighbors.append(right)
		if bottom and not bottom.visited:
			neighbors.append(bottom)
		if left and not left.visited:
			neighbors.append(left)
		return choice(neighbors) if neighbors else False

def remove_walls(current, next):
	dx = current.x - next.x
	if dx == 1:
		current.walls["left"] = False
		next.walls["right"] = False
	elif dx == -1:
		current.walls["right"] = False
		next.walls["left"] = False
	dy = current.y - next.y
	if dy == 1:
		current.walls["top"] = False
		next.walls["bottom"] = False
	elif dy == -1:
		current.walls["bottom"] = False
		next.walls["top"] = False

def get_smooth_path_points(path, tile_size):
	"""Преобразует путь из клеток в плавные координаты с центрами клеток"""
	return [(x * tile_size + tile_size // 2, y * tile_size + tile_size // 2) for x, y in path]

grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []
maze_generated = False
def find_shortest_path(start, end):
	queue = deque()
	queue.append((start.x, start.y, []))
	visited = set()
	visited.add((start.x, start.y))

	while queue:
		x, y, path = queue.popleft()
		current_cell = grid_cells[x + y * cols]

		if x == end.x and y == end.y:
			return path + [(x, y)]

		# Проверяем всех соседей
		for dx, dy, direction in [(0, -1, "top"), (1, 0, "right"), (0, 1, "bottom"), (-1, 0, "left")]:
			nx, ny = x + dx, y + dy
			if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in visited:
				if not current_cell.walls[direction]:
					visited.add((nx, ny))
					queue.append((nx, ny, path + [(x, y)]))
	
	return []  # Если путь не найден

grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
current_cell = grid_cells[0]
stack = []

def player():

	# Игрок

	player_x, player_y = 0, 0
	player_size = TILE - 4
	goal_x, goal_y = cols - 1, rows - 1
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
	
		# Управление игроком
		keys = pygame.key.get_pressed()
		current_cell = grid_cells[player_x + player_y * cols]
	
		if keys[pygame.K_UP] and not current_cell.walls["top"]:
			player_y = max(0, player_y - 1)
		if keys[pygame.K_RIGHT] and not current_cell.walls["right"]:
			player_x = min(cols - 1, player_x + 1)
		if keys[pygame.K_DOWN] and not current_cell.walls["bottom"]:
			player_y = min(rows - 1, player_y + 1)
		if keys[pygame.K_LEFT] and not current_cell.walls["left"]:
			player_x = max(0, player_x - 1)
	
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
	
		# Отрисовка игрока
		pygame.draw.rect(win, pygame.Color("green"), 
						(player_x * TILE + 2, player_y * TILE + 2, player_size, player_size))
	
		# Отрисовка цели
		if SHOW_FLAG:
			win.blit(pygame.transform.scale(pygame.image.load("Flag.png"), (TILE, TILE)), (goal_x * TILE + 2, goal_y * TILE + 2))
	
		# Проверка достижения цели
		if player_x == goal_x and player_y == goal_y:
			font = pygame.font.SysFont(None, 55)
			text = font.render("You Win!", True, pygame.Color("white"))
			win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
	
		pygame.display.flip()
		clock.tick(20)
		
# Находим кратчайший путь
def show_path():
	
	# Находим кратчайший путь
	start_cell = grid_cells[0]
	end_cell = grid_cells[-1]
	shortest_path = find_shortest_path(start_cell, end_cell)
	smooth_path = get_smooth_path_points(shortest_path, TILE)

	# Параметры анимации
	player_pos = smooth_path[0] if smooth_path else (0, 0)
	player_size = TILE - 4
	path_index = 0
	animation_speed = 0.5  # Скорость движения игрока
	t = 0  # Параметр интерполяции

	path_index = 0
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
	
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
	
		# Отрисовка пути линией
		if SHOW_PATH_LINE and len(smooth_path) > 1:
			pygame.draw.lines(win, pygame.Color("green"), False, smooth_path, 3)
	
		if SHOW_FLAG:
			win.blit(pygame.transform.scale(pygame.image.load("Flag.png"), (TILE, TILE)), ((cols - 1) * TILE + 2, (rows - 1) * TILE + 2))
	
		# Анимация движения игрока
		if path_index < len(smooth_path) - 1:
			start_point = smooth_path[path_index]
			end_point = smooth_path[path_index + 1]
		
			player_pos = (
				start_point[0] + (end_point[0] - start_point[0]) * t,
				start_point[1] + (end_point[1] - start_point[1]) * t
			)
		
			t += animation_speed
			if t >= 1.0:
				t = 0
				path_index += 1
		else:
			font = pygame.font.SysFont(None, 55)
			text = font.render("Path Completed!", True, pygame.Color("white"))
			win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
	
		pygame.draw.rect(win, pygame.Color("yellow"), 
						(player_pos[0] - player_size//2, player_pos[1] - player_size//2, 
						 player_size, player_size))
	
		pygame.display.flip()
		clock.tick(30)

# Тут создаётся кукусик
goal_x, goal_y = cols - 1, rows - 1
def get_possible_actions(x, y):
	cell = grid_cells[x + y * cols]
	actions = []
	if not cell.walls["top"] and y > 0:
		actions.append(0)  # up
	if not cell.walls["right"] and x < cols - 1:
		actions.append(1)  # right
	if not cell.walls["bottom"] and y < rows - 1:
		actions.append(2)  # down
	if not cell.walls["left"] and x > 0:
		actions.append(3)  # left
	return actions

def get_next_position(x, y, action):
	if action == 0:  # up
		return x, y - 1
	elif action == 1:  # right
		return x + 1, y
	elif action == 2:  # down
		return x, y + 1
	elif action == 3:  # left
		return x - 1, y
	return x, y

class QLearningAgent:
	def __init__(self, maze_width, maze_height, x=0):
		self.x = x
		self.y = 0
		self.q_table = np.zeros((maze_width, maze_height, 4))
		self.actions = [0, 1, 2, 3]  # 0: up, 1: right, 2: down, 3: left
		self.alpha = 0.1
		self.gamma = 0.9
		self.epsilon = 1.0
		self.epsilon_decay = 0.995
		self.epsilon_min = 0.01
		self.goal_x = maze_width - 1
		self.goal_y = maze_height - 1
		self.steps_without_progress = 0
		self.max_steps_without_progress = 50
		self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.goal_x = cols - 1
		self.goal_y = rows - 1
		if x != 0:
			self.goal_x = x
			self.goal_y = rows - 1

	def calculate_distance(self, x, y):
		"""Вычисляет расстояние до цели через волновой алгоритм либо теорему Пифагора"""
		
		if SIMPLE_DISTANCE:
			return sqrt((self.goal_x - self.x)**2 + (self.goal_y - self.y)**2)

		distances = np.full((cols, rows), -1)
		queue = deque()
		queue.append((self.goal_x, self.goal_y))
		distances[self.goal_x, self.goal_y] = 0
	
		while queue:
			cx, cy = queue.popleft()
			for dx, dy, direction in [(0, -1, "top"), (1, 0, "right"), 
									 (0, 1, "bottom"), (-1, 0, "left")]:
				nx, ny = cx + dx, cy + dy
				if 0 <= nx < cols and 0 <= ny < rows and distances[nx, ny] == -1:
					cell = grid_cells[cx + cy * cols]
					if not cell.walls[direction]:
						distances[nx, ny] = distances[cx, cy] + 1
						queue.append((nx, ny))
	
		return distances[x, y] if distances[x, y] != -1 else 1000

	def get_reward(self, x, y, new_x, new_y):

		if new_x == self.goal_x and new_y == self.goal_y:
			return 100
	
		# Получаем список возможных действий из новой позиции
		possible_actions = get_possible_actions(new_x, new_y)
	
		# Штраф за тупик
		if len(possible_actions) == 1 and (new_x != x or new_y != y):
			return -1
	
		old_dist = self.calculate_distance(x, y)
		new_dist = self.calculate_distance(new_x, new_y)
	
		if new_dist < old_dist:
			return 0.7  # Награда за уменьшение реального расстояния
		elif new_dist > old_dist:
			return -0.7  # Штраф за увеличение расстояния
		else:
			return -0.2  # Небольшой штраф за шаг на месте

		
	def get_state_index(self, x, y):
		return x, y
	
	def choose_action(self, x, y, possible_actions):
		if random() < self.epsilon:
			# Исследование: случайное действие из возможных
			try:
				return choice(possible_actions)
			except:
				pass
		else:
			# Использование: лучшее действие из Q-таблицы
			state = self.get_state_index(x, y)
			q_values = [self.q_table[state[0], state[1], a] if a in possible_actions else -np.inf 
					   for a in self.actions]
			return np.argmax(q_values)
	
	def update_q_table(self, x, y, action, reward, next_x, next_y):
		current_state = self.get_state_index(x, y)
		next_state = self.get_state_index(next_x, next_y)
		
		# Q-learning формула
		best_next_action = np.argmax(self.q_table[next_state[0], next_state[1]])
		td_target = reward + self.gamma * self.q_table[next_state[0], next_state[1], best_next_action]
		td_error = td_target - self.q_table[current_state[0], current_state[1], action]
		self.q_table[current_state[0], current_state[1], action] += self.alpha * td_error
		
		# Уменьшаем epsilon
		self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

def smooth_move(start_pos, end_pos, duration, current_time, speed_factor):
	
	# Корректируем время с учетом множителя скорости
	adjusted_time = current_time * speed_factor
	adjusted_duration = duration / speed_factor
	
	t = min(adjusted_time / adjusted_duration, 1.0)
	# Квадратичная easing функция
	t = t * t * (3 - 2 * t)
	return (
		start_pos[0] + (end_pos[0] - start_pos[0]) * t,
		start_pos[1] + (end_pos[1] - start_pos[1]) * t
	)

def animate_agent_path(agent, start_pos, goal_pos, path=[], keys=[]):

	global direction
	x, y = start_pos
	visited = set()
	if path == []:
		path = [start_pos]
		# Построение пути по Q-таблице
		while (x, y) != goal_pos and len(path) < cols * rows:
			visited.add((x, y))
			possible_actions = get_possible_actions(x, y)
			if not possible_actions:
				break
		
			# Выбираем действие с максимальным Q-значением
			action = np.argmax(agent.q_table[x, y])
			new_x, new_y = get_next_position(x, y, action)
		
			if (new_x, new_y) in visited:
				break  # Предотвращаем зацикливание
		
			path.append((new_x, new_y))
			x, y = new_x, new_y
	
	# Визуализация плавного движения
	if len(path) < 2:
		return
	
	segment_duration = 0.1  # Длительность движения между точками (в секундах)
	current_segment = 0
	segment_start_time = pygame.time.get_ticks() / 1000
	running = True

	frames_list = []
	tick = 0
	num = 0
	del_key = None
	key_deleted = False
	while running and current_segment < len(path) - 1:

		tick += 1
		distance = 0
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		
		# Плавное перемещение между текущей и следующей точкой
		try:
			while path[current_segment][0] == path[current_segment + distance][0] or path[current_segment][1] == path[current_segment + distance][1]:
				distance += 1
				start_cell = path[current_segment]
				end_cell = path[current_segment + distance - 1]
				if end_cell[2] and not key_deleted:
					del_key = (end_cell[0], end_cell[1] + 1)

			if end_cell[0] < start_cell[0]:
				direction = False
			if end_cell[0] > start_cell[0]:
				direction = True
		except:
			start_cell = path[current_segment]
			end_cell = path[-1]
		current_time = (pygame.time.get_ticks() / 1000 - segment_start_time) / (max(abs(end_cell[0] - start_cell[0]), abs(end_cell[1] - start_cell[1])) + 1)
		start_px = (start_cell[0] * TILE + TILE // 2, start_cell[1] * TILE + TILE // 2)
		end_px = (end_cell[0] * TILE + TILE // 2, end_cell[1] * TILE + TILE // 2)
		player_pos = smooth_move(start_px, end_px, segment_duration, current_time, 1)

		if del_key is not None and player_pos[0] // TILE == del_key[0] and player_pos[1] // TILE == del_key[1]:
			try:
				keys.remove((player_pos[0] // TILE, player_pos[1] // TILE))
				print(keys, (player_pos[0] // TILE, player_pos[1] // TILE))
			except:
				pass
			del_key = None
			key_deleted = True
		
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
		if SHOW_PATH_LINE:
			lines_path = [(p[0]*TILE+TILE//2, p[1]*TILE+TILE//2) for p in path[:current_segment]]
			lines_path.append(start_px)
			lines_path.append((int(player_pos[0]), int(player_pos[1])))
			try: pygame.draw.lines(win, pygame.Color("black"), False, lines_path, 3)
			except:pass
		# Финиш
		for key in keys:
			pygame.draw.circle(win, (150, 150, 150), (key[0] * TILE + TILE / 2, key[1] * TILE + TILE / 2), TILE * 0.2)
		win.blit(kukusik_right if direction else kukusik_left, (int(player_pos[0] - TILE / 2 + TILE * 0.15), int(player_pos[1] - TILE / 2 + TILE * 0.15)))
		pygame.display.flip()
		
		pygame.image.save(win, f"animation_frames/{tick:05}.png")
		
		# Переход к следующему сегменту
		if player_pos == end_px:
			current_segment += distance - 1
			segment_start_time = pygame.time.get_ticks() / 1000
			del_key = None

	height_map = win.copy()

	os.system('ffmpeg -i "animation_frames/%05d.png" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 23 "Agent path.mp4"')

	for filename in os.listdir("animation_frames"):
		file_path = os.path.join("animation_frames", filename)
		os.remove(file_path)
	
	for map_x, map_y in product(range(WIDTH), range(HEIGHT)):
		if height_map.get_at((map_x, map_y)) == pygame.Color("blue"):
			height_map.set_at((map_x, map_y), (255, 255, 255))
		else:
			height_map.set_at((map_x, map_y), (0, 0, 0))
	pygame.image.save(height_map, "Height map.png")

def animate_agents_path(pathes):

	global direction
	# Визуализация плавного движения
	
	segment_duration = 0.1  # Длительность движения между точками
	current_segments = [0] * len(pathes)
	segment_start_time = pygame.time.get_ticks() / 1000
	running = True
	print([len(path) for path in pathes])
	frames_list = []
	tick = 0
	
	while running:
	
		tick += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
		
		current_time = pygame.time.get_ticks() / 1000 - segment_start_time

		kukusik_ends = True
		for i, path in enumerate(pathes):
			# Плавное перемещение между текущей и следующей точкой
			distance = 0
			current_segment = current_segments[i]
			try:
				path[current_segment + 2]
				try:
					while path[current_segment][0] == path[current_segment + distance][0] or path[current_segment][1] == path[current_segment + distance][1]:
						distance += 1
						start_cell = path[current_segment]
						end_cell = path[current_segment + distance - 1]

					if end_cell[0] < start_cell[0]:
						direction = False
					if end_cell[0] > start_cell[0]:
						direction = True
				except Exception:
					start_cell = path[current_segment]
					end_cell = path[-1]
				start_px = (start_cell[0] * TILE + TILE // 2, start_cell[1] * TILE + TILE // 2)
				end_px = (end_cell[0] * TILE + TILE // 2, end_cell[1] * TILE + TILE // 2)
				player_pos = smooth_move(start_px, end_px, segment_duration, current_time, 1)
				win.blit(kukusik_right if direction else kukusik_left, (int(player_pos[0] - TILE / 2 + TILE * 0.15), int(player_pos[1] - TILE / 2 + TILE * 0.15)))

				pygame.image.save(win, f"animation_frames/{tick:05}.png")

				# Переход к следующему сегменту
				if player_pos == end_px:
					current_segments[i] += distance - 1
					segment_start_time = pygame.time.get_ticks() / 1000
				kukusik_ends = False
			except:
				pass
		
		if kukusik_ends:
			break
		pygame.display.flip()
		
		# Захват кадра для видео
		if SAVE_KUKUSIK_PATH:
			frame_data = pygame.surfarray.array3d(win)
			frame_data = frame_data.swapaxes(0, 1)
			frames_list.append(frame_data)

	height_map = win.copy()

	# Сохранение пути в видео

	if SAVE_KUKUSIK_PATH:
		os.system('ffmpeg -i "animation_frames/%05d.png" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 23 "AI race.mp4"')
		
		for filename in os.listdir("animation_frames"):
			file_path = os.path.join("animation_frames", filename)
			os.remove(file_path)

	for map_x, map_y in product(range(WIDTH), range(HEIGHT)):
		if height_map.get_at((map_x, map_y)) == pygame.Color("blue"):
			height_map.set_at((map_x, map_y), (255, 255, 255))
		else:
			height_map.set_at((map_x, map_y), (0, 0, 0))
	pygame.image.save(height_map, "Height map.png")

def AI():

	global direction

	agent = QLearningAgent(cols, rows)
	start_x, start_y = 0, 0
	goal_x, goal_y = cols - 1, rows - 1
	player_x, player_y = start_x, start_y
	episodes = 5
	path = []
	episode = 0
	successful_episodes = 0

	while episode < episodes:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
	
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
	
		# Отрисовка финиша
		if SHOW_FLAG:
			win.blit(pygame.transform.scale(pygame.image.load("Flag.png"), (TILE, TILE)), (goal_x * TILE + 2, goal_y * TILE + 2))
	
		# Получаем возможные действия
		possible_actions = get_possible_actions(player_x, player_y)
	
		# Выбираем действие
		action = agent.choose_action(player_x, player_y, possible_actions)
	
		# Получаем новую позицию
		new_x, new_y = get_next_position(player_x, player_y, action)
		if new_x < agent.x:
			direction = False
		if new_x > agent.x:
			direction = True

		win.blit(kukusik_right if direction else kukusik_left, (player_x * TILE + TILE * 0.15, player_y * TILE + TILE * 0.15))
	
		# Вычисляем награду
		reward = agent.get_reward(player_x, player_y, new_x, new_y)
	
		# Обновляем Q-таблицу
		agent.update_q_table(player_x, player_y, action, reward, new_x, new_y)
	
		# Обновляем позицию игрока
		player_x, player_y = new_x, new_y
	
		# Проверяем завершение эпизода
		path.append((player_x, player_y))
		pygame.display.flip()
		if (player_x == goal_x and player_y == goal_y) or len(possible_actions) == 0:
			episode += 1
			player_x, player_y = start_x, start_y
		
			# Отображаем статистику
			print(f"Episode: {episode}/{episodes}  Success: {successful_episodes}  Epsilon: {agent.epsilon:.2f}")
			path = []
		clock.tick(20)
	# После обучения показываем оптимальный путь
		
	player_x, player_y = start_x, start_y
	path = [(player_x, player_y)]
	animate_agent_path(agent, (start_x, start_y), (goal_x, goal_y))

def AI_race():

	global direction

	agents = [QLearningAgent(cols, rows, int(cols // 10 * (i + 1))) for i in range(10)]
	pathes = [[] for _ in range(10)]

	# Основной цикл обучения
	while True:
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
	
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]

		for i, agent in enumerate(agents):
			if agent != "":

				# Получаем возможные действия
				possible_actions = get_possible_actions(agent.x, agent.y)
	
				# Выбираем действие
				action = agent.choose_action(agent.x, agent.y, possible_actions)
	
				# Получаем новую позицию
				new_x, new_y = get_next_position(agent.x, agent.y, action)
				if new_x < agent.x:
					direction = False
				if new_x > agent.x:
					direction = True

				win.blit(kukusik_right if direction else kukusik_left, (agent.x * TILE + TILE * 0.15, agent.y * TILE + TILE * 0.15))
				# Вычисляем награду
				reward = agent.get_reward(agent.x, agent.y, new_x, new_y)
	
				# Обновляем Q-таблицу
				agent.update_q_table(agent.x, agent.y, action, reward, new_x, new_y)
	
				# Обновляем позицию игрока
				agent.x, agent.y = new_x, new_y
				pathes[i].append((agent.x, agent.y))
				# Проверяем завершение эпизода
				if (agent.x == agent.goal_x and agent.y == agent.goal_y):
					agent.x, agent.y = agent.x, 0
					print(f"Кукусик #{agents.index(agent) + 1} добрался!")
					agents[i] = ""
					if all([ag == "" for ag in agents]):
						animate_agents_path(pathes)
						quit()

		pygame.display.flip()

def get_distance(x, y, goal_x, goal_y):

	distances = np.full((cols, rows), -1)
	queue = deque()
	queue.append((goal_x, goal_y))
	distances[goal_x, goal_y] = 0
	
	while queue:
		cx, cy = queue.popleft()
		for dx, dy, direction in [(0, -1, "top"), (1, 0, "right"), 
								 (0, 1, "bottom"), (-1, 0, "left")]:
			nx, ny = cx + dx, cy + dy
			if 0 <= nx < cols and 0 <= ny < rows and distances[nx, ny] == -1:
				cell = grid_cells[cx + cy * cols]
				if not cell.walls[direction]:
					distances[nx, ny] = distances[cx, cy] + 1
					queue.append((nx, ny))
	
	return distances[x, y] if distances[x, y] != -1 else 1000  # Большое число если путь не существует

def AI_with_keys():

	global direction

	agent = QLearningAgent(cols, rows)
	start_x, start_y = 0, 0
	player_x, player_y = start_x, start_y

	keys = [(randint(0, cols - 1), randint(0, rows - 1)) for _ in range(15)]
	shortest_path_key = keys[0]
	shortest_path = get_distance(player_x, player_y, keys[0][0], keys[0][1])
	for key in keys:
		path_to_key = get_distance(player_x, player_y, key[0], key[1])
		if path_to_key < shortest_path:
			shortest_path = path_to_key
	last_x, last_y = 0, 0
	agent.goal_x, agent.goal_y = shortest_path_key
	path = []
	keys_list = keys.copy()

	# Основной цикл обучения
	episode = 0
	successful_episodes = 0

	while True:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
		deleted_key = False
		# Отрисовка
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
	
		# Отрисовка финиша
		if SHOW_FLAG:
			win.blit(pygame.transform.scale(pygame.image.load("Flag.png"), (TILE, TILE)), ((cols - 1) * TILE + 2, (rows - 1) * TILE + 2))
		
		for key in keys:
			pygame.draw.circle(win, (150, 150, 150), (key[0] * TILE + TILE / 2, key[1] * TILE + TILE / 2), TILE * 0.2)

		# Получаем возможные действия
		possible_actions = get_possible_actions(player_x, player_y)
	
		# Выбираем действие
		action = agent.choose_action(player_x, player_y, possible_actions)
	
		# Получаем новую позицию
		new_x, new_y = get_next_position(player_x, player_y, action)
		if new_x < agent.x:
			direction = False
		if new_x > agent.x:
			direction = True

		win.blit(kukusik_right if direction else kukusik_left, (player_x * TILE + TILE * 0.15, player_y * TILE + TILE * 0.15))
	
		# Вычисляем награду
		reward = agent.get_reward(player_x, player_y, new_x, new_y)
		if (last_x, last_y) == (new_x, new_y): reward -= 4
		if (player_x, player_y) == (agent.goal_x, agent.goal_y):
			if keys == []:
				animate_agent_path(agent, (start_x, start_y), (goal_x, goal_y), path, keys=keys_list)
				quit()
			else:
				if (agent.goal_x, agent.goal_y) == (cols - 1, rows - 1):

					if keys == []:
						agent.goal_x, agent.goal_y = cols - 1, rows - 1
					else:
						shortest_path_key = keys[0]
						shortest_path = get_distance(player_x, player_y, keys[0][0], keys[0][1])
						for key in keys:
							path_to_key = get_distance(player_x, player_y, key[0], key[1])
							if path_to_key < shortest_path:
								shortest_path = path_to_key

						agent.goal_x, agent.goal_y = shortest_path_key

				else:
					keys.remove((agent.goal_x, agent.goal_y))
					deleted_key = True
					agent.goal_x, agent.goal_y = cols - 1, rows - 1
	
		# Теперь надо обновить Q-таблицу
		agent.update_q_table(player_x, player_y, action, reward, new_x, new_y)
	
		# Новая позиция кукусика
		last_x, last_y = player_x, player_y
		player_x, player_y = new_x, new_y
		path.append((player_x, player_y, deleted_key))
		pygame.display.flip()

if CHAOS_LABIRINT:
	for _ in range(10000):
		cell = grid_cells[randint(0, len(grid_cells) - 1)]
		cell.walls[["top" if cell.y > 0 else "", "right" if cell.x < rows else "", "botom" if cell.y < cols else "", "left"][randint(0, 3)]] = False # TODO починить
else:

	generation_tick = 0

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
				
		win.fill(pygame.Color("gray"))
		[cell.draw() for cell in grid_cells]
		current_cell.visited = True
		current_cell.draw_current_cell()
		
		next_cell = current_cell.check_neighbors()
		if next_cell:
			next_cell.visited = True
			stack.append(current_cell)
			remove_walls(current_cell, next_cell)
			current_cell = next_cell
		elif stack:
			current_cell = stack.pop()
		else:
			# Сохранить генерацию лабиринта, если надо
			if SAVE_LABIRINT_GENERATING:
				os.system('ffmpeg -i "animation_frames/%05d.png" -r 30 -c:v libx264 -pix_fmt yuv420p -crf 23 output_video.mp4')
			
				for filename in os.listdir("animation_frames"):
					file_path = os.path.join("animation_frames", filename)
					os.remove(file_path)
			break
	
		pygame.display.flip()
	
		# Захваfкадра для видео
		if SAVE_LABIRINT_GENERATING:
			pygame.image.save(win, f"animation_frames/{generation_tick:05}.png")

AI()
