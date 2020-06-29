"""
Arcade program that uses the classes in universe.py
Inspired by the One Lone Coder's video on Procedurally Generated Universes
"""

# Imports
import arcade
from universe import Universe
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

# Constants
SECTOR_SIZE = 50
SECTORS_X = SCREEN_WIDTH / SECTOR_SIZE
SECTORS_Y = SCREEN_HEIGHT / SECTOR_SIZE
SCREEN_TITLE = "Dawson's Universe"
MOVEMENT_SPEED = 7
UNIVERSE_SIZE = 1
DECELERATION = 0.25

# Check SECTORS_X and SECTORS_Y are equal, comparing float to int
if int(SECTORS_X) != SECTORS_X or int(SECTORS_Y) != SECTORS_Y:
    raise Exception("Adjust screen width, height, or sector size")
else:
    SECTORS_X = int(SECTORS_X)
    SECTORS_Y = int(SECTORS_Y)


class UniverseApp(arcade.Window):
    """User starts with a black screen with random stars around.
    Navigation with WASD, new stars procedurally generated around.
    Returning to the same galaxy_offset yields the same procedurally
    generated stars."""

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def setup(self):
        arcade.set_background_color(arcade.color.BLACK)

        # controls the place you're shown within the entire galaxy
        # starts in the middle of the galaxy, x and y should be negative
        self.galaxy_offset = {"x": -(UNIVERSE_SIZE * SCREEN_WIDTH / 2), "y": -(UNIVERSE_SIZE * SCREEN_HEIGHT / 2),
                              "dx": 0, "dy": 0}

        # starHovered - is a star being hovered over? hovered_star - the location of that star in memory
        self.starHovered = False
        self.hovered_star = None

        # boolean to know when to show star window
        self.selected_star = None

        self.universe = Universe(SECTORS_X * UNIVERSE_SIZE, SECTORS_Y * UNIVERSE_SIZE, SECTOR_SIZE)

        # create planet list and populate with random planets
        self.star_list = arcade.ShapeElementList()

        for count_x, star_list in enumerate(self.universe.starsystems):
            for count_y, star in enumerate(star_list):
                if star.star_exists:
                    x_pos = SCREEN_WIDTH / 2 - SECTOR_SIZE * (0.5 * SECTORS_X - count_x)
                    y_pos = SCREEN_HEIGHT / 2 - SECTOR_SIZE * (0.5 * SECTORS_Y - count_y)
                    shape = arcade.create_ellipse_filled_with_colors(x_pos, y_pos, star.star_diameter,
                                                                     star.star_diameter, star.star_color,
                                                                     star.star_color)
                    self.star_list.append(shape)

        # menu that shows up when you click on a star
        self.star_menu = arcade.ShapeElementList()
        outer = arcade.create_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, SCREEN_WIDTH - 30,
                                               (SCREEN_HEIGHT / 2) - 30, arcade.color.AIR_FORCE_BLUE)
        self.star_menu.append(outer)
        inner = arcade.create_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, SCREEN_WIDTH - 50,
                                               (SCREEN_HEIGHT / 2) - 50, arcade.color.EERIE_BLACK)
        self.star_menu.append(inner)

        # draw boundary lines
        self.boundary_lines = arcade.ShapeElementList()
        # bottom line
        line = arcade.create_line(0, 0, UNIVERSE_SIZE * SCREEN_WIDTH, 0, arcade.color.WHITE, line_width=5)
        self.boundary_lines.append(line)
        # left line
        line = arcade.create_line(0, 0, 0, UNIVERSE_SIZE * SCREEN_HEIGHT, arcade.color.WHITE, line_width=5)
        self.boundary_lines.append(line)
        # top line
        line = arcade.create_line(0, UNIVERSE_SIZE * SCREEN_HEIGHT, UNIVERSE_SIZE * SCREEN_WIDTH,
                                  UNIVERSE_SIZE * SCREEN_HEIGHT, arcade.color.WHITE, line_width=5)
        self.boundary_lines.append(line)
        # right line
        line = arcade.create_line(UNIVERSE_SIZE * SCREEN_WIDTH, UNIVERSE_SIZE * SCREEN_HEIGHT,
                                  UNIVERSE_SIZE * SCREEN_WIDTH, 0, arcade.color.WHITE, line_width=5)
        self.boundary_lines.append(line)

        # TODO: Create newly generated sectors somehow, Minecraft style

    def on_draw(self):
        """Called whenever you draw your window, about every 10 ms"""
        # Clear the screen and start drawing
        arcade.start_render()

        # draw stars
        self.star_list.draw()

        # draw boundary lines
        self.boundary_lines.draw()

        # draw selection circle
        if self.starHovered or self.selected_star is not None:
            arcade.draw_circle_outline(self.hovered_star.x + self.galaxy_offset["x"],
                                       self.hovered_star.y + self.galaxy_offset["y"],
                                       self.hovered_star.star_diameter + 10, arcade.color.YELLOW)

        # green square is the player, which "moves"
        self.player = arcade.draw_rectangle_filled(SCREEN_WIDTH / 2,
                                                   SCREEN_HEIGHT / 2, 10, 10, arcade.color.YELLOW_GREEN)

        # draw the selection menu and planets
        if self.selected_star is not None:
            PADDING = 30
            self.star_menu.draw()
            arcade.draw_text(str(self.selected_star), PADDING, (SCREEN_WIDTH / 2) - 30, arcade.color.WHITE, 24,
                             anchor_x="left", anchor_y="top")
            self.planet_list.draw()

    def on_update(self, delta_time: float):
        """Handles the screen that pops up for selected stars"""

        # Calculate deceleration
        if abs(self.galaxy_offset["dx"]) > DECELERATION:
            if self.galaxy_offset["dx"] > 0:
                self.galaxy_offset["dx"] -= DECELERATION
            else:
                self.galaxy_offset["dx"] += DECELERATION
        else:
            self.galaxy_offset["dx"] = 0

        if abs(self.galaxy_offset["dy"]) > DECELERATION:
            if self.galaxy_offset["dy"] > 0:
                self.galaxy_offset["dy"] -= DECELERATION
            else:
                self.galaxy_offset["dy"] += DECELERATION
        else:
            self.galaxy_offset["dy"] = 0

        # Calculate dy and dx
        # Notice - movement is opposite of typical
        # We are moving the background, not the player
        if self.up_pressed and not self.down_pressed:
            self.galaxy_offset["dy"] = -MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.galaxy_offset["dy"] = MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.galaxy_offset["dx"] = MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.galaxy_offset["dx"] = -MOVEMENT_SPEED

        # Adjust galaxy_offset based on dy and dx
        self.galaxy_offset["x"] += self.galaxy_offset["dx"]
        self.galaxy_offset["y"] += self.galaxy_offset["dy"]

        # Adjust stars relative to galaxy_offset
        self.star_list.center_x = self.galaxy_offset["x"]
        self.star_list.center_y = self.galaxy_offset["y"]

        # Adjust boundary lines relative to galaxy_offset
        self.boundary_lines.center_x = self.galaxy_offset["x"]
        self.boundary_lines.center_y = self.galaxy_offset["y"]

    def on_key_press(self, symbol: int, modifiers: int):
        """Handles keypress events, WASD to move, Q to quit"""
        if symbol == 113:  # "q" to quit
            exit(0)

        if symbol == 119:  # "w"
            self.up_pressed = True
        elif symbol == 97:  # "a"
            self.left_pressed = True
        elif symbol == 115:  # "s"
            self.down_pressed = True
        elif symbol == 100:  # "d"
            self.right_pressed = True
        elif symbol == 103:  # "g"
            print(self.galaxy_offset)

    def on_key_release(self, symbol: int, modifiers: int):
        # Resets speed to 0
        if symbol == 119:  # "w"
            self.up_pressed = False
        elif symbol == 97:  # "a"
            self.left_pressed = False
        elif symbol == 115:  # "s"
            self.down_pressed = False
        elif symbol == 100:  # "d"
            self.right_pressed = False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """Called when the user moves the mouse, handles the appearance of a selection circle
        when you hover over a star
        """
        # boolean to keep track of if a star system is found at the mouse's position
        star_found = False

        # Find star that the mouse is clicking at and update hovered variables so it can be drawn
        for star_list in self.universe.starsystems:
            for star in star_list:
                true_x = star.x + self.galaxy_offset["x"]
                true_y = star.y + self.galaxy_offset["y"]

                # if star exists and you're clicking it
                if star.star_exists:
                    x_hover = abs(x - true_x) < (star.star_diameter / 2)
                    y_hover = abs(y - true_y) < (star.star_diameter / 2)
                    if x_hover and y_hover:
                        star_found = True

                        self.starHovered = True
                        self.hovered_star = star

        if not star_found:
            self.starHovered = False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Called when the mouse is pressed"""
        if self.starHovered:
            # generate the system, system remained ungenerated for memory efficiency
            self.hovered_star.generate_system()
            # copy the state of the newly generated star system
            self.selected_star = self.hovered_star

            # create ShapeElementList of all of the planets surrounding the star
            self.planet_list = arcade.ShapeElementList()
            for i, p in enumerate(self.selected_star.planets):
                planet = arcade.create_ellipse_filled(p.distance, SCREEN_HEIGHT / 4, p.diameter, p.diameter,
                                                      p.color)
                self.planet_list.append(planet)
        else:
            self.selected_star = None


if __name__ == "__main__":
    window = UniverseApp(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
    arcade.close_window()
