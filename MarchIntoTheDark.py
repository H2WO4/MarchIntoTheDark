# Imports
from __future__ import annotations
from typing import Dict, List, Tuple

import pygame
from pygame.event import Event
from pygame.surface import Surface

from random import choice, choices, shuffle

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


# Define all the objects pertaining to the Rooms
class RoomType:
	"""
	The RoomType class define a specific type of room.
	"""
	listAll: Dict[str, RoomType] = {}
	weights: Dict[RoomType, float] = {}

	basicType: RoomType

	def __init__(self, name: str, color: Color, weight: float = 0) -> None:
		self.name = name
		self.color = color

		RoomType.listAll[name] = self
		RoomType.weights[self] = weight

	@classmethod
	def getType(cls, name: str) -> RoomType:
		"""
		Return the RoomType with the given name.
		"""
		return cls.listAll[name]

	@classmethod
	def getRandomType(cls) -> RoomType:
		"""
		Return a random room type.
		"""
		# Obtain a random room type
		typeList = list(cls.listAll.values())
		weightList = [cls.weights[t] for t in typeList]

		return choices(typeList, weightList)[0]

class Room:
	"""
	The Room class define a room of the dungeon.\n
	A room is an atom of the dungeon.\n
	It require a certain type, a RoomType, to know how to act.
	"""
	# Define the list of all rooms
	listAll: List[Room] = []

	def __init__(self, type: RoomType, pos: Tuple[int, int]) -> None:
		"""
		Create a room with the given type and position.
		"""
		# Set the room type, and position
		self.type = type
		self.x, self.y = pos

		self.neighborCount = 0

		# Add the room to the list of all rooms
		Room.listAll.append(self)
	
	def render(self, surface: Surface) -> None:
		"""
		Render the room on the given surface.
		"""
		# If the room is the current room, render the current room symbol
		if self.x == 0 and self.y == 0:
			pygame.draw.rect(surface, (255, 0, 0), (surface.get_width() // 2 + 30 * self.x - 10, surface.get_height() // 2 + 30 * self.y - 10, 30, 30), 0)

		# Draw the room at its position, with the given color
		pygame.draw.rect(surface, self.type.color, (surface.get_width() // 2 + 30 * self.x - 5, surface.get_height() // 2 + 30 * self.y - 5, 20, 20), 0)

	@staticmethod
	def basicRoom(x: int, y: int) -> Room:
		"""
		Create a blank room at the given position.
		"""
		return Room(RoomType.basicType, (x, y))


# Define all the objects pertaining to the Dungeon
class Dungeon:
	"""
	The Dungeon class define a dungeon.\n
	It is a collection of rooms.
	"""
	# Define a way to obtain the currently active dungeon
	activeDungeon: Dungeon

	def __init__(self, size: int) -> None:
		"""
		Create a dungeon of the given size.
		"""
		# Create the dungeon
		self.rooms: Dict[Tuple[int, int], Room] = {}

		# Add the entrance
		self.rooms[0, 0] = Room.basicRoom(0, 0)

		# Special case for the entrance
		for direction in range(4):
			# Convert the direction to a vector
			vX, vY = dirNumToVector(direction)

			# Create the new room, and add it to the dungeon
			newRoom = Room.basicRoom(vX, vY)
			self.rooms[vX, vY] = newRoom

			# Set its neighbor count
			newRoom.neighborCount = 1

		# Set the number of neighbors of the entrance
		self.rooms[0, 0].neighborCount = 4

		# While the dungeon is not full, or the pity is not too high
		i = 0
		while i < size:
			# Get a random room
			baseRoom = choice(list(self.rooms.values()))

			# Get a list of all the possible directions, and shuffle it
			directionList = list(range(4))
			shuffle(directionList)

			# For each direction in the list
			for direction in directionList:
				# Convert the direction to a vector, and use them to obtain the coordinates of the new room
				vX, vY = dirNumToVector(direction)
				nX, nY = baseRoom.x + vX, baseRoom.y + vY

				# Obtain the list of neighbors the new room would have
				neighbors = [self.rooms.get((nX + x, nY + y)) for x, y in (dirNumToVector(d) for d in range(4))]
				neighbors = [n for n in neighbors if n]

				# If there would only be one neighbor, and the new room is not already in the dungeon, add it
				if len(neighbors) == 1 and (nX, nY) not in self.rooms:
					# Create the new room, and add it to the dungeon
					newRoom = Room.basicRoom(nX, nY)
					self.rooms[nX, nY] = newRoom

					# Set its neighbor count
					newRoom.neighborCount = 1

					for room in neighbors:
						# Increase the neighbor count of the neighbor
						room.neighborCount += 1

					# Increment the number of rooms generated, and break the loop
					i += 1
					break
		
		# Set up the central room as the entrance
		self.rooms[0, 0].type = RoomType.getType("Entrance")

		# Generate the special rooms
		for room in [r for r in self.rooms.values() if r.neighborCount == 1]:
			# Set the room type to a random room type
			room.type = RoomType.getRandomType()

		# Define this dungeon as the active dungeon
		Dungeon.activeDungeon = self

	def render(self, surface: Surface) -> None:
		"""
		Render the dungeon on the given surface.
		"""
		for room in self.rooms.values():
			room.render(surface)





# Define the main game object
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
	# Create the game instance
	MarchIntoTheDark = Instance()
	# Set up the FPS clock
	pygame.time.Clock().tick(30)

	# Define unique room types
	EntranceType = RoomType("Entrance", (255, 255, 0))

	# Define the basic room type
	BasicType = RoomType("Basic", (255, 255, 255), 3)
	RoomType.basicType = BasicType

	# Define the special room types
	LibraryType = RoomType("Library", (0, 200, 0), 1)
	PlanetariumType = RoomType("Planetarium", (0, 200, 200), 1)
	LabType = RoomType("Lab", (200, 0, 0), 1)
	GreenhouseType = RoomType("Greenhouse", (200, 0, 200), 1)
	
	# Create the dungeon
	A = Dungeon(100)

	# Run the game
	MarchIntoTheDark.on_execute()