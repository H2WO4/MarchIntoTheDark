# Imports
from __future__ import annotations
from typing import List, Tuple
import pygame
from pygame.event import Event
from pygame.rect import Rect
from pygame.surface import Surface

Color = Tuple[int, int, int] | Tuple[int, int, int, int]

class RoomType:
	"""
	The RoomType class define a specific type of room.\n
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
		self.type = type
		self.x, self.y = pos

		Room.listAll.append(self)
		MarchIntoTheDark


class Instance:
	def __init__(self) -> None:
		self._running = True
		self._display_surf: Surface
		self.size = self.weight, self.height = 640, 400

		self.sprites: List[Rect] = []
		self.i = 0

	def on_init(self) -> None:
		pygame.init()
		self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
		self._running = True

	def on_event(self, event: Event) -> None:
		match event.type:
			case pygame.QUIT:
				self._running = False

	def on_loop(self) -> None:
		pass

	def on_render(self) -> None:

		for ro in Room.listAll:
			self.sprites.append(pygame.draw.rect(self._display_surf, ro.type.color, (0, self.i, 200, 100), 5))
			self.i += 10
		
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

if __name__ == "__main__":
	MarchIntoTheDark = Instance()
	pygame.time.Clock().tick(60)

	Basic = RoomType("Basic", (255, 0, 0))
	Test = Room(Basic, (0, 0))

	MarchIntoTheDark.on_execute()