# Imports
from __future__ import annotations
from typing import Dict, List, Tuple

import pygame
from pygame.event import Event
from pygame.surface import Surface

from random import choice, choices, randint

# Define types
Color = Tuple[int, int, int] | Tuple[int, int, int, int]

# Define helper functions
def dirNumToVector(dirNum: int) -> Tuple[int, int]:
	match dirNum:
		case 0:
			return (0, 1)
		case 1:
			return (1, 0)
		case 2:
			return (0, -1)
		case 3:
			return (-1, 0)
		case _:
			raise ValueError(f"Invalid direction number: {dirNum}")



class RoomType:
	"""
	The RoomType class define a specific type of room.
	"""
	listAll: Dict[str, RoomType] = {}
	weights: Dict[RoomType, float] = {}

	def __init__(self, name: str, color: Color, weight: float = 0) -> None:
		self.name = name
		self.color = color

		RoomType.listAll[name] = self
		RoomType.weights[self] = weight

class Room:
	"""
	The Room class define a room of the dungeon.\n
	A room is an atom of the dungeon.\n
	It require a certain type, a RoomType, to know how to act.
	"""
	listAll: List[Room] = []

	def __init__(self, type: RoomType, pos: Tuple[int, int]) -> None:
		"""
		Create a room with the given type and position.
		"""
		self.type = type
		self.x, self.y = pos

		self.neighbors: List[Room | None] = [None, None, None, None]
		self.nNeighbors = 0

		Room.listAll.append(self)
	
	def render(self, surface: Surface) -> None:
		"""
		Render the room on the given surface.
		"""
		if self.x == 0 and self.y == 0:
			pygame.draw.rect(surface, (255, 0, 0), (surface.get_width() // 2 + 30 * self.x - 10, surface.get_height() // 2 + 30 * self.y - 10, 30, 30), 0)
		
		pygame.draw.rect(surface, self.type.color, (surface.get_width() // 2 + 30 * self.x - 5, surface.get_height() // 2 + 30 * self.y - 5, 20, 20), 0)

	@staticmethod
	def randomRoom(x: int, y: int) -> Room:
		"""
		Create a random room with the given position.
		"""
		typeList = list(RoomType.listAll.values())
		weightList = [RoomType.weights[t] for t in typeList]
		return Room(choices(typeList, weightList)[0], (x, y))


class Dungeon:
	"""
	The Dungeon class define a dungeon.\n
	It is a collection of rooms.
	"""
	activeDungeon: Dungeon

	def __init__(self, size: int) -> None:
		"""
		Create a dungeon of the given size.
		"""
		self.rooms: Dict[Tuple[int, int], Room] = {}

		self.rooms[0, 0] = Room(RoomType.listAll["Entrance"], (0, 0))

		i = 0
		pity = 0
		while i < size:
			baseRoom = choice(list(self.rooms.values()))
			if baseRoom.nNeighbors < 3:
				direction = randint(0, 3)
				if baseRoom.neighbors[direction] is None:
					nX, nY = dirNumToVector(direction)
					newRoom = Room.randomRoom(baseRoom.x + nX, baseRoom.y + nY)
					self.rooms[newRoom.x, newRoom.y] = newRoom

					baseRoom.neighbors[direction] = newRoom
					newRoom.neighbors[(direction + 2) % 4] = baseRoom

					baseRoom.nNeighbors += 1
					i += 1
		
		
		Dungeon.activeDungeon = self

	def render(self, surface: Surface) -> None:
		"""
		Render the dungeon on the given surface.
		"""
		for room in self.rooms.values():
			room.render(surface)





# Display
class Instance:
	def __init__(self) -> None:
		self._running = True
		self.size = self.weight, self.height = 900, 600
		self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
		pygame.display.set_caption('March Into The Dark')

	def on_init(self) -> None:
		pygame.init()
		self._running = True

	def on_event(self, event: Event) -> None:
		match event.type:
			case pygame.QUIT:
				self._running = False
			
			case pygame.KEYDOWN:
				match event.key:
					case pygame.K_ESCAPE:
						self._running = False
					
					case pygame.K_UP:
						for room in Room.listAll:
							room.y += 1
					
					case pygame.K_DOWN:
						for room in Room.listAll:
							room.y -= 1
					
					case pygame.K_LEFT:
						for room in Room.listAll:
							room.x += 1
					
					case pygame.K_RIGHT:
						for room in Room.listAll:
							room.x -= 1

	def on_loop(self) -> None:
		pass

	def on_render(self) -> None:
		self._display_surf.fill((0, 0, 0))

		Dungeon.activeDungeon.render(self._display_surf)
		
		pygame.display.update()

	def on_cleanup(self) -> None:
		pygame.quit()

	def on_execute(self) -> None:
		if self.on_init() == False:
			self._running = False

		while (self._running):
			for event in pygame.event.get():
				self.on_event(event)

			self.on_loop()
			self.on_render()

		self.on_cleanup()


# Main
if __name__ == "__main__":
	MarchIntoTheDark = Instance()
	pygame.time.Clock().tick(30)

	BasicType = RoomType("Basic", (200, 200, 200), 1)
	FloodedType = RoomType("Flooded", (0, 0, 200), 0.1)
	PoisonedType = RoomType("Poisoned", (0, 200, 0), 0.1)
	DarkType = RoomType("Dark", (127, 127, 127), 0.2)
	
	EmptyType = RoomType("Empty", (100, 0, 0))
	EntranceType = RoomType("Entrance", (200, 200, 0))

	A = Dungeon(100)

	MarchIntoTheDark.on_execute()