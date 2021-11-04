# Imports
from __future__ import annotations
from typing import Dict, List, Tuple

import pygame
from pygame.event import Event
from pygame.surface import Surface

import random

# Define types
Color = Tuple[int, int, int] | Tuple[int, int, int, int]


class RoomType:
	"""
	The RoomType class define a specific type of room.
	"""
	listAll: Dict[str, RoomType] = {}

	def __init__(self, name: str, color: Color, special: bool = False) -> None:
		self.name = name
		self.color = color
		self.special = special

		RoomType.listAll[name] = self

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

		Room.listAll.append(self)
	
	def render(self, surface: Surface) -> None:
		"""
		Render the room on the given surface.
		"""
		pygame.draw.rect(surface, self.type.color, (surface.get_width() // 2 + 30 * self.x, surface.get_height() // 2 + 30 * self.y, 20, 20), 0)

	@staticmethod
	def randomRoom(x: int, y: int) -> Room:
		"""
		Create a random room with the given position.
		"""
		return Room(random.choice([type for type in RoomType.listAll.values() if not type.special]), (x, y))


class Dungeon:
	"""
	The Dungeon class define a dungeon.\n
	It is a collection of rooms.
	"""
	activeDungeon: Dungeon = None # type: ignore

	def __init__(self, x: int, y: int) -> None:
		"""
		Create a dungeon of the given size.
		"""
		self.x, self.y = x, y
		self.rooms: Dict[int, Dict[int, Room]] = {}

		for i in range(-x, x+1):
			self.rooms[i] = {}
			for j in range(-y, y+1):
				self.rooms[i][j] = Room.randomRoom(i, j)

		self.rooms[0][0].type = RoomType.listAll["Entrance"]

		Dungeon.activeDungeon = self

	def render(self, surface: Surface) -> None:
		"""
		Render the dungeon on the given surface.
		"""
		for line in self.rooms.values():
			for room in line.values():
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
							room.y -= 1
					
					case pygame.K_DOWN:
						for room in Room.listAll:
							room.y += 1
					
					case pygame.K_LEFT:
						for room in Room.listAll:
							room.x -= 1
					
					case pygame.K_RIGHT:
						for room in Room.listAll:
							room.x += 1

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

	BasicType = RoomType("Basic", (255, 255, 255))
	FloodedType = RoomType("Flooded", (0, 0, 255))
	PoisonedType = RoomType("Poisoned", (0, 255, 0))

	EntranceType = RoomType("Entrance", (255, 255, 0), True)

	A = Dungeon(5, 5)

	MarchIntoTheDark.on_execute()