# Imports
from __future__ import annotations
from typing import List, Tuple

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
	listAll: List[RoomType] = []

	def __init__(self, name: str, color: Color) -> None:
		self.name = name
		self.color = color

		RoomType.listAll.append(self)

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
		pygame.draw.rect(surface, self.type.color, (20 * self.x, 20 * self.y, 20, 20), 0)

	@staticmethod
	def randomRoom(x: int, y: int) -> Room:
		"""
		Create a random room with the given position.
		"""
		return Room(random.choice(RoomType.listAll), (x, y))


class Dungeon:
	"""
	The Dungeon class define a dungeon.
	"""
	def __init__(self, size: Tuple[int, int]) -> None:
		"""
		Create a dungeon of the given size.
		"""
		self.size = size
		self.rooms: List[Room] = []

		for x in range(self.size[0]):
			for y in range(self.size[1]):
				self.rooms.append(Room.randomRoom(x, y))

	def render(self, surface: Surface) -> None:
		"""
		Render the dungeon on the given surface.
		"""
		for room in self.rooms:
			room.render(surface)





# Display
class Instance:
	def __init__(self) -> None:
		self._running = True
		self.size = self.weight, self.height = 640, 400
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


		for room in Room.listAll:
			room.render(self._display_surf)
		
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

	Basic = RoomType("Basic", (255, 0, 0))
	Test = Room(Basic, (0, 0))

	MarchIntoTheDark.on_execute()