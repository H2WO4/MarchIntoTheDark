# Imports
from __future__ import annotations
from typing import Callable, Dict, List, Tuple

import pygame
from pygame.event import Event
from pygame.surface import Surface

from random import choice, choices, randint, shuffle

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
	_listAll: Dict[str, RoomType] = {}
	_listSpecial: Dict[str, RoomType] = {}
	_weights: Dict[RoomType, Callable[..., float]] = {}

	basicType: RoomType

	def __init__(self, name: str, color: Color, special: bool = False) -> None:
		self.name = name
		self.color = color

		RoomType._listAll[name] = self
		if special:
			RoomType._listSpecial[name] = self

	@classmethod
	def getType(cls, name: str) -> RoomType:
		"""
		Return the RoomType with the given name.
		"""
		return cls._listAll[name]

	@classmethod
	def addWeight(cls, roomType: str, weight: Callable[..., float]) -> None:
		"""
		Add a weight to the given room type.
		"""
		cls._weights[cls.getType(roomType)] = weight

	@classmethod
	def getRandomType(cls, distance: int, numberOcc: Dict[RoomType, int], size: int) -> RoomType:
		"""
		Return a random room type, with the given number of neighbors, distance, and number of occurrences.
		"""
		# Get the weights of each room type
		weights = {t: cls._weights[t](t, distance, numberOcc, size) for t in cls._listSpecial.values()}

		# Return a random room type, weighted by the weights
		return choices(list(weights.keys()), list(weights.values()), k=1)[0]


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
		self.distanceFromEntrance = 0

		# Add the room to the list of all rooms
		Room.listAll.append(self)

	def render(self, surface: Surface) -> None:
		"""
		Render the room on the given surface.
		"""
		# If the room is the current room, render the current room symbol
		if self.x == 0 and self.y == 0:
			pygame.draw.rect(surface, (127, 127, 127), (surface.get_width() // 2 + 30 * self.x - 15, surface.get_height() // 2 + 30 * self.y - 15, 30, 30), 0)

		# Draw the room at its position, with the given color
		pygame.draw.rect(surface, self.type.color, (surface.get_width() // 2 + 30 * self.x - 10, surface.get_height() // 2 + 30 * self.y - 10, 20, 20), 0)

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
		self.roomTypes: Dict[RoomType, int] = {}

		# Add the entrance
		self.rooms[0, 0] = Room.basicRoom(0, 0)

		# Special case for the entrance, forces 2 to 4 neighbors
		directions = [0, 1, 2, 3]
		shuffle(directions)
		baseRooms = randint(2, 4)
		for direction in directions[:baseRooms]:
			# Convert the direction to a vector
			vX, vY = dirNumToVector(direction)

			# Create the new room, and add it to the dungeon
			newRoom = Room.basicRoom(vX, vY)
			self.rooms[vX, vY] = newRoom

			# Set its neighbor count, and distance from the entrance
			newRoom.neighborCount = 1
			newRoom.distanceFromEntrance = 1

		# Set the number of neighbors of the entrance
		self.rooms[0, 0].neighborCount = baseRooms

		# While the dungeon is not full
		i = baseRooms
		while i < size:
			# Get a random room, apart from the entrance
			baseRoom = choice(list(self.rooms.values())[1:])

			# Get a list of all the possible directions, and shuffle it
			directionList = list(range(4))
			shuffle(directionList)

			# For each direction in the list
			for direction in directionList:
				# Convert the direction to a vector, and use them to obtain the coordinates of the new room
				vX, vY = dirNumToVector(direction)
				nX, nY = baseRoom.x + vX, baseRoom.y + vY

				# Obtain the list of neighbors the new room would have
				neighbors = [self.rooms[nX + x, nY + y] for x, y in (dirNumToVector(d) for d in range(4)) if (nX + x, nY + y) in self.rooms]

				# If there would only be one neighbor, and the new room is not already in the dungeon, add it
				if len(neighbors) == 1 and (nX, nY) not in self.rooms:
					# Create the new room, and add it to the dungeon
					newRoom = Room.basicRoom(nX, nY)
					self.rooms[nX, nY] = newRoom

					# Set its neighbor count, and distance from the entrance
					newRoom.neighborCount = 1
					newRoom.distanceFromEntrance = min([r.distanceFromEntrance for r in neighbors]) + 1

					for room in neighbors:
						# Increase the neighbor count of the neighbor
						room.neighborCount += 1

					# Increment the number of rooms generated, and break the for loop
					i += 1
					break

		# Set up the central room as the entrance
		self.rooms[0, 0].type = RoomType.getType("Entrance")

		# Search for all the dead ends
		deadEnds = [r for r in self.rooms.values() if r.neighborCount == 1]
		# Sort them by distance from the entrance
		deadEnds.sort(key = lambda r: r.distanceFromEntrance)

		# Take the furthest dead end, and set it as the stairs
		deadEnds[-1].type = RoomType.getType("Stairs")
		# Take it out of the list
		del deadEnds[-1]

		shuffle(deadEnds)
		# For each remaing dead end
		for room in deadEnds:
			# Get a random room type
			newType = RoomType.getRandomType(room.distanceFromEntrance, self.roomTypes, size)

			# Assign it to the room
			room.type = newType
			# Increase the count of the room type
			self.roomTypes[newType] = self.roomTypes.get(newType, 0) + 1

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
	RoomType("Entrance", (255, 255, 0))
	RoomType("Stairs", (255, 0, 0))

	# Define the basic room type
	RoomType.basicType = RoomType("Basic", (255, 255, 255))

	# Define the special room types
	RoomType("Greenhouse", (0, 255, 0), True)
	RoomType.addWeight("Greenhouse", lambda *_: 1)

	RoomType("Treasury", (0, 0, 255), True)
	RoomType.addWeight("Treasury", lambda *_: 0.5)

	RoomType("Library", (0, 255, 255), True)
	RoomType.addWeight("Library", lambda *_: 1)

	RoomType("Temple", (255, 0, 255), True)
	RoomType.addWeight("Temple", lambda *_: 1)

	# Create the dungeon
	A = Dungeon(300)

	# Log the respective number of rooms of each type
	print([(t.name, n) for t, n in A.roomTypes.items()])

	# Run the game
	MarchIntoTheDark.on_execute()
