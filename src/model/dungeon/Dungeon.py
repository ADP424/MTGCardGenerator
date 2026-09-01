import re

from PIL import Image, ImageChops, ImageDraw

from constants import (
    BELEREN_BOLD,
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_FRAMES,
    CARD_RULES_TEXT,
    FRAMES_PATH,
)
from log import log
from model.Layer import Layer
from model.regular.RegularCardSmall import RegularCardSmall
from utils import (
    add_drop_shadow,
    allocate_by_weight,
    alpha_composite_clipped,
    apply_alpha_mask,
    load_font,
    open_image,
    paste_image,
    replace_ticks,
    str_to_float,
    subtract_intervals,
    union_alpha_channel,
)


class Dungeon(RegularCardSmall):
    """
    A layered image representing a dungeon card (Adventures in the Forgotten Realms style), with all
    relevant card metadata.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

    base_width : int, optional
        The width of the root image. Determined by the frame layout in the metadata if not given.

    base_height : int, optional
        The height of the root image. Determined by the frame layout in the metadata if not given.

    art_layer : Layer, optional
        The art to use in the art slot of the frame. Renders first, before the frame layers.

    frame_layers : list[Layer], optional
        The layers of card frames. Lower-index layers are rendered first. Renders after art, before collector info.

    collector_layers : list[Layer], optional
        The layers of collector info. Lower-index layers are rendered first. Renders after frames, before text.

    text_layers : list[Layer], optional
        The layers of card text. Lower-index layers are rendered first. Renders after collector info and frames.

    overlay_layers : list[Layer], optional
        Any additional layers to render above everything else on the card. Rendered absolutely last.
    """

    class Room:
        """
        A single room of a dungeon.

        Attributes
        ----------
        index : int
            Starts at 1, based on the room's position in the rules text. Works as an identifier for rooms without names.

        ids : list[str], optional
            Every identifier this room can be targeted with using `{to=...}`.

        name : str, optional
            The title of the dungeon room.

        body : str, optional
            The room's rules text.

        span : float, default: 1.0
            Relative width within the room's row.

        rowspan : int, default: 1
            How many rows tall the room is. Begins in the current row, then spans downward.

        pixel_height_multiplier : float | None, optional
            Multiplier on the row's automatically computed height, or None for no multiplier.

        starts_row : bool, default: False
            Whether this room begins a new row.

        door_targets : list[str] | None, optional
            The list of identifiers of rooms this room leads to.

        arrows : bool, default: True
            Whether this room's doorways get direction arrows.

        row : int, default: 0
            0-based index of the row the room starts in.

        min_columns : int, default: 0
            The fewest tile columns the room may be, wide enough to hold the doorways on its busier edge.

        tile_x0 : int, default: 0
            The furthest left column, in tiles, the room touches.

        tile_y0 : int, default: 0
            The furthest up row, in tiles, the room touches.

        tile_x1 : int, default: 0
            The furthest right column, in tiles, the room touches.

        tile_y1 : int, default: 0
            The furthest down row, in tiles, the room touches.

        pixel_x : int, default: 0
            The furthest left pixel the room touches.

        pixel_y : int, default: 0
            The furthest up pixel the room touches.

        pixel_width : int, default: 0
            The width of the room in pixels.

        pixel_height : int, default: 0
            The height of the room in pixels.

        top_pixel_gaps : list[tuple[int, int]], optional
            The ranges of pixels where doorways clip the room's top walls away.

        bottom_pixel_gaps : list[tuple[int, int]], optional
            The ranges of pixels where doorways clip the room's bottom walls away.

        left_pixel_gaps : list[tuple[int, int]], optional
            The ranges of pixels where doorways clip the room's left wall away.

        right_pixel_gaps : list[tuple[int, int]], optional
            The ranges of pixels where doorways clip the room's right wall away.

        inline : bool, default: False
            Whether the name and the rules text share a single line.

        name_font_size : int, default: 0
            The font sizes of the room's name/title.

        body_font_size : int, default: 0
            The font size of the room's rules text.

        name_pixel_box : tuple[int, int, int, int], default: (0, 0, 0, 0)
            The pixel rectange the room's name is drawn in.

        body_pixel_box : tuple[int, int, int, int], default: (0, 0, 0, 0)
            The pixel rectange the room's body text is drawn in.
        """

        def __init__(self, index: int):
            self.index = index
            self.ids: list[str] = []
            self.name = ""
            self.body = ""
            self.span = 1.0
            self.rowspan = 1
            self.pixel_height_multiplier: float | None = None
            self.starts_row = False
            self.door_targets: list[str] | None = None
            self.arrows = True
            self.row = 0
            self.min_columns = 0
            self.tile_x0 = 0
            self.tile_y0 = 0
            self.tile_x1 = 0
            self.tile_y1 = 0
            self.pixel_x = 0
            self.pixel_y = 0
            self.pixel_width = 0
            self.pixel_height = 0
            self.top_pixel_gaps: list[tuple[int, int]] = []
            self.bottom_pixel_gaps: list[tuple[int, int]] = []
            self.left_pixel_gaps: list[tuple[int, int]] = []
            self.right_pixel_gaps: list[tuple[int, int]] = []
            self.inline = False
            self.name_font_size = 0
            self.body_font_size = 0
            self.name_pixel_box = (0, 0, 0, 0)
            self.body_pixel_box = (0, 0, 0, 0)

        @property
        def label(self) -> str:
            return self.name if self.name else f"room #{self.index}"

    class Door:
        """
        A doorway through the wall between two adjacent rooms: either a horizontal doorway (in the
        wall between a room and the one directly below it) or a vertical doorway (in the wall
        between a room and one directly beside it). Its opening is a whole number of tiles wide,
        sits on tile boundaries, and is stored in tile units. `Dungeon` is responsible for
        converting it to pixels.

        Attributes
        ----------
        axis : str
            `"horizontal"` for a doorway in a top/bottom wall (seam is a row boundary, opening
            runs along columns), or `"vertical"` for a doorway in a left/right wall (seam is a
            column boundary, opening runs along rows).

        tile_x0 : int
            For a horizontal doorway, the first tile column of the opening. For a vertical
            doorway, the tile column of the wall seam itself.

        tile_x1 : int
            For a horizontal doorway, the tile column just past the end of the opening (exclusive
            end). Unused for a vertical doorway.

        tile_y : int
            For a horizontal doorway, the grid row of the wall seam. For a vertical doorway, the
            first tile row of the opening.

        tile_y1 : int
            For a vertical doorway, the tile row just past the end of the opening (exclusive end).
            Unused for a horizontal doorway.

        show_arrow : bool
            Whether to draw a direction arrow in this doorway.

        arrow_direction : str
            Which way the direction arrow should point: `"down"` (or, for an `ExpandedDungeonLocal`
            cross-card doorway, `"up"`) for a horizontal doorway, or `"left"`/`"right"` for a
            vertical doorway (the direction from the room whose `{to=...}` named the other, toward
            that other room) -- or `"up_down"`/`"left_right"` (matching axis) for a doorway both
            rooms name each other in, drawn with a double-headed arrow instead of a single-headed
            one that would otherwise arbitrarily point from whichever room was visited first.

        split_half : str | None, default: None
            For a doorway whose seam is a physical card boundary rather than an interior row/column
            (an `ExpandedDungeonLocal` cross-card doorway), which half of the doorway
            piece this card shows: for a horizontal doorway, `"top"` (the card above the seam) or
            `"bottom"` (the card below it); for a vertical doorway, `"left"` (the card left of the
            seam) or `"right"` (the card right of it); `None` for an ordinary same-card doorway
            that shows the whole piece.
        """

        def __init__(
            self,
            tile_x0: int,
            tile_x1: int,
            tile_y: int,
            show_arrow: bool,
            axis: str = "horizontal",
            tile_y1: int = 0,
            arrow_direction: str = "down",
            split_half: str | None = None,
        ):
            self.axis = axis
            self.tile_x0 = tile_x0
            self.tile_x1 = tile_x1
            self.tile_y = tile_y
            self.tile_y1 = tile_y1
            self.show_arrow = show_arrow
            self.arrow_direction = arrow_direction
            self.split_half = split_half

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCardSmall"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        super().__init__(
            metadata,
            art_layer,
            frame_layers,
            collector_layers,
            text_layers,
            overlay_layers,
        )

        # Dungeon-specific regex for unique dungeon placeholders
        self.DUNGEON_PLACEHOLDER_REGEX = self._get_dungeon_placeholder_regex()

        # Title Box
        self.TITLE_BOX_X = 90
        self.TITLE_BOX_Y = 105
        self.TITLE_BOX_WIDTH = 1313
        self.TITLE_BOX_HEIGHT = 114
        self.TITLE_X = 128
        self.TITLE_BOTTOM_Y = 200
        self.TITLE_WIDTH = 1244

        # Title Text
        self.TITLE_FONT_COLOR = (
            (255, 255, 255)
            if "white" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            and "light" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
            else (0, 0, 0)
        )
        self.TITLE_TEXT_ALIGN = "center"

        # Tile Grid
        self._init_grid_constants()

        # Room Constraints
        self.MIN_ROOM_COLUMNS = 2
        self.MIN_ROW_TILES = 2

        # Room Content
        self.ROOM_CONTENT_INSET_X = 32
        self.ROOM_CONTENT_INSET_Y = 32
        self.ROOM_TEXT_CENTERED = True
        self.ROOM_TEXT_MAX_FONT_SIZE = 52
        self.ROOM_TEXT_MIN_FONT_SIZE = 8
        self.ROOM_TEXT_UNIFORM_FONT_SIZE = True  # use one size for every room, like the real cards
        self.ROOM_INLINE_SEPARATOR_SPACES = 4  # gap between an inline name and its rules text
        self.ROOM_INLINE_WIDTH_SLACK = 4
        self.ROOM_NAME_FONT = BELEREN_BOLD
        self.ROOM_NAME_FONT_SCALE = 1.15  # the name is always a little bigger than the rules text
        self.ROOM_NAME_MAX_FONT_SIZE = 64
        self.ROOM_NAME_MIN_FONT_SIZE = 10
        self.ROOM_NAME_FONT_COLOR = (0, 0, 0)
        self.ROOM_NAME_OUTLINE_SIZE = 0
        self.ROOM_NAME_DROP_SHADOW_OFFSET = (0, 0)
        self.ROOM_NAME_GAP = 2  # the rules text engine adds its own margin on top of this

        # Rules Text
        self.RULES_TEXT_MAX_FONT_SIZE = self.ROOM_TEXT_MAX_FONT_SIZE
        self.RULES_TEXT_MIN_FONT_SIZE = self.ROOM_TEXT_MIN_FONT_SIZE
        self.RULES_TEXT_FONT_COLOR = (0, 0, 0)

        # Rules Box
        self.RULES_BOX_X = self.GRID_ORIGIN_X
        self.RULES_BOX_Y = self.GRID_ORIGIN_Y
        self.RULES_BOX_WIDTH = self.GRID_COLUMNS * self.TILE_SIZE
        self.RULES_BOX_HEIGHT = self.GRID_ROWS * self.TILE_SIZE
        self.WATERMARK_HEIGHT_TO_RULES_TEXT_HEIGHT_SCALE = 0.35

        # Walls, doorways, and arrows
        self._init_wall_constants()

        # Power & Toughness Text
        self.POWER_TOUGHNESS_X = float("inf")
        self.POWER_TOUGHNESS_Y = float("inf")

        # Other
        self.HOLO_STAMP_X = float("inf")
        self.HOLO_STAMP_Y = float("inf")

        self._wall_piece_cache: dict[str, Image.Image | None] = {}
        self._body_measurement_cache: dict[tuple[int, int, int], tuple[int, int, int, int] | None] = {}
        self._row_tile_heights: list[int] = []

        # The rest of __init__ parses everything up front

        # Pull wall-texture frame lines (and their masks) out of CARD_FRAMES
        self.wall_texture_frames: list[tuple[str, list[str]]] = []
        self.non_wall_frames: str = self.get_metadata(CARD_FRAMES)

        pending_masks: list[str] = []
        textures: list[tuple[str, list[str]]] = []
        kept: list[str] = []

        for line in self.get_metadata(CARD_FRAMES).split("\n"):
            path = line.lower().strip()
            if not path:
                continue
            if path.startswith(self.WALL_TEXTURE_PREFIX):
                textures.append((path, pending_masks.copy()))
                pending_masks.clear()
                continue
            if "mask/" in path:
                pending_masks.append(path)
                continue
            kept.extend(pending_masks)
            pending_masks.clear()
            kept.append(path)

        kept.extend(pending_masks)
        self.wall_texture_frames = textures
        self.non_wall_frames = "\n".join(kept)

        # Split the rules text on {end} and group into rows
        self.rooms: list["Dungeon.Room"] = []
        self.rows: list[list["Dungeon.Room"]] = []
        self.room_ids: dict[str, "Dungeon.Room"] = {}

        def apply_room_directives(room: "Dungeon.Room", directives: list[tuple[str, str]]) -> bool:
            """
            Apply parsed directives to a room. Returns whether the room was marked nameless.
            """

            nameless = False
            for key, value in directives:
                if key in ("row", "newrow"):
                    room.starts_row = True
                elif key == "id":
                    room.ids.extend(v.strip().lower() for v in value.split(",") if v.strip())
                elif key == "span":
                    parsed = str_to_float(value, default=None)
                    if parsed is None:
                        log(f"Can't parse '{value}' as a room span.")
                    else:
                        room.span = max(parsed, 0.01)
                elif key == "rowspan":
                    parsed = str_to_float(value, default=None)
                    if parsed is None:
                        log(f"Can't parse '{value}' as a room rowspan.")
                    else:
                        room.rowspan = max(int(round(parsed)), 1)
                elif key == "height":
                    parsed = str_to_float(value, default=None)
                    if parsed is None:
                        log(f"Can't parse '{value}' as a row height multiplier.")
                    else:
                        room.pixel_height_multiplier = max(parsed, 0.01)
                elif key in ("to", "door", "doors"):
                    if room.door_targets is None:
                        room.door_targets = []
                    room.door_targets.extend(self._parse_door_targets(value))
                elif key in ("nameless", "noname"):
                    nameless = True
                elif key == "noarrow":
                    room.arrows = False
                elif key == "arrow":
                    room.arrows = True
            return nameless

        text = self.get_metadata(CARD_RULES_TEXT)
        if text and "{skip}" not in text:
            pending_row = False
            for section in re.split(r"\{end\}", text, flags=re.IGNORECASE):
                room = Dungeon.Room(len(self.rooms) + 1)
                directives: list[tuple[str, str]] = []

                def capture(match: re.Match) -> str:
                    directives.append(
                        (
                            match.group(1).lower().replace("-", "").replace("arrows", "arrow"),
                            (match.group(2) or "").strip(),
                        )
                    )
                    return ""

                body = self.DUNGEON_PLACEHOLDER_REGEX.sub(capture, section)
                nameless = apply_room_directives(room, directives)

                lines = body.split("\n")
                while lines and not lines[0].strip():
                    lines.pop(0)
                while lines and not lines[-1].strip():
                    lines.pop()

                if not lines:
                    pending_row = pending_row or room.starts_row
                    continue

                if not nameless:
                    room.name = lines.pop(0).strip()
                    while lines and not lines[0].strip():
                        lines.pop(0)
                room.body = "\n".join(lines).strip()

                if pending_row:
                    room.starts_row = True
                    pending_row = False

                room.ids.append(str(room.index))
                if room.name:
                    room.ids.append(room.name.lower())
                self.rooms.append(room)

            for room in self.rooms:
                if not self.rows or room.starts_row:
                    self.rows.append([])
                self.rows[-1].append(room)
                room.row = len(self.rows) - 1

            for room in self.rooms:
                room.rowspan = max(1, min(room.rowspan, len(self.rows) - room.row))
                for identifier in room.ids:
                    if identifier not in self.room_ids:
                        self.room_ids[identifier] = room

        # Compute every room's tile-grid rectangle, pixel rectangle, font sizes, and text boxes
        self.doors: list["Dungeon.Door"] = []

        if self.rows:

            # Give every room a min_columns wide enough for its explicit {to=...} doorways
            bottom_doors: dict[int, int] = {room.index: 0 for room in self.rooms}
            top_doors: dict[int, int] = {room.index: 0 for room in self.rooms}
            for upper, lower, _, _ in self._horizontal_door_pairs():
                bottom_doors[upper.index] += 1
                top_doors[lower.index] += 1

            for room in self.rooms:
                capacity = max(bottom_doors[room.index], top_doors[room.index]) * self.DOOR_MIN_SHARED_COLUMNS
                room.min_columns = max(room.min_columns, capacity)

            # Give every row a min_rows tall enough for any explicit {to=...} doorway
            self._vertical_door_pair_rows: list[tuple[int, int]] = []
            for room, other in self._vertical_door_pairs():
                overlap_start = max(room.row, other.row)
                overlap_end = min(room.row + room.rowspan, other.row + other.rowspan)
                self._vertical_door_pair_rows.append((overlap_start, overlap_end))

            # Widths come before heights so a wider room wraps its text into fewer lines
            self._compute_room_widths()
            self._adjust_room_widths_for_text()
            self._compute_row_heights()
            self._finalize_room_rects()

            # Pick the font size for each room (optionally unifying them) and lay its text out
            if self.rooms:

                def find_room_font_size(room: "Dungeon.Room") -> int:
                    """
                    Return the largest rules text font size whose layout fits inside the room.
                    """

                    content_width = max(room.pixel_width - 2 * self.ROOM_CONTENT_INSET_X, 1)
                    content_height = max(room.pixel_height - 2 * self.ROOM_CONTENT_INSET_Y, 1)

                    for size in range(self.ROOM_TEXT_MAX_FONT_SIZE, self.ROOM_TEXT_MIN_FONT_SIZE - 1, -1):
                        if self._measure_room_content(room, size, content_width)["height"] <= content_height:
                            return size

                    log(f"The text of '{room.label}' doesn't fit in its room, even at the minimum font size.")
                    return self.ROOM_TEXT_MIN_FONT_SIZE

                def layout_room(room: "Dungeon.Room", body_size: int):
                    """
                    Place a room's name and rules text at the given font size, centering them together
                    inside the room. An inline name shares its baseline with the rules text.
                    """

                    content_x = room.pixel_x + self.ROOM_CONTENT_INSET_X
                    content_y = room.pixel_y + self.ROOM_CONTENT_INSET_Y
                    content_width = max(room.pixel_width - 2 * self.ROOM_CONTENT_INSET_X, 1)
                    content_height = max(room.pixel_height - 2 * self.ROOM_CONTENT_INSET_Y, 1)

                    metrics = self._measure_room_content(room, body_size, content_width)
                    room.body_font_size = body_size
                    room.name_font_size = metrics["name_size"]
                    room.inline = metrics["inline"]

                    name_height = metrics["name_ascent"] + metrics["name_descent"]
                    margin = metrics["margin"]

                    if room.inline:
                        group_ascent = max(metrics["name_ascent"], metrics["body_ascent"])
                        group_descent = max(metrics["name_descent"], metrics["body_descent"])
                        group_width = metrics["name_width"] + metrics["separator_width"] + metrics["body_width"]
                        top = content_y + max((content_height - (group_ascent + group_descent)) // 2, 0)
                        baseline = top + group_ascent
                        start_x = content_x + max((content_width - group_width) // 2, 0)

                        room.name_pixel_box = (
                            start_x,
                            baseline - metrics["name_ascent"],
                            metrics["name_width"] + 2,
                            name_height,
                        )

                        # Counteract the margining done in RegularCard (because Dungeon text gets closer)
                        room.body_pixel_box = (
                            start_x + metrics["name_width"] + metrics["separator_width"] - margin,
                            baseline - metrics["body_ascent"] - margin,
                            metrics["body_width"] + 2 * margin + self.ROOM_INLINE_WIDTH_SLACK,
                            metrics["content_height"] + 2 * margin,
                        )

                    elif room.body:
                        body_height = metrics["content_height"] + 2 * margin
                        name_block = name_height + (self.ROOM_NAME_GAP if room.name else 0)
                        top = content_y + max((content_height - (name_block + body_height)) // 2, 0)
                        room.name_pixel_box = (content_x, top, content_width, name_height)
                        room.body_pixel_box = (content_x, top + name_block, content_width, body_height)
                    else:
                        top = content_y + max((content_height - name_height) // 2, 0)
                        room.name_pixel_box = (content_x, top, content_width, name_height)
                        room.body_pixel_box = (content_x, top, content_width, 0)

                sizes = [find_room_font_size(room) for room in self.rooms]
                if self.ROOM_TEXT_UNIFORM_FONT_SIZE:
                    sizes = [min(sizes)] * len(sizes)
                for room, size in zip(self.rooms, sizes):
                    layout_room(room, size)

        # Put a doorway in the wall between each room and every room directly above or below it
        # the same seam to a mutual "up_down" when both rooms name each other.
        arrows_on = "arrowless" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])
        opening = self.DOOR_OPENING_COLUMNS
        minimum = self.DOOR_MIN_SHARED_COLUMNS
        built_horizontal: dict[frozenset, "Dungeon.Door"] = {}

        for room in self.rooms:
            targets = self._door_targets_for(room, log_problems=True)
            for other in sorted(targets, key=lambda r: r.tile_x0):
                shared_c0, shared_c1 = self._get_shared_wall_columns(room, other)
                shared = shared_c1 - shared_c0
                if shared < minimum:
                    log(
                        f"'{room.label}' and '{other.label}' only share {shared} tile(s) of wall, but a "
                        f"doorway needs {minimum}. Widen one of the rooms, or leave them without a doorway."
                    )
                    continue

                # Center the opening on the shared wall, snapped to a whole tile column
                tile_x0 = shared_c0 + (shared - opening) // 2
                tile_x0 = self._adjust_door_opening(tile_x0, shared_c0, shared_c1, axis="horizontal")
                door = Dungeon.Door(
                    tile_x0, tile_x0 + opening, room.tile_y1, arrows_on and room.arrows, axis="horizontal"
                )
                self.doors.append(door)
                built_horizontal[frozenset((room.index, other.index))] = door

        for upper, lower, named_down, named_up in self._horizontal_door_pairs():
            if not named_up:
                continue
            key = frozenset((upper.index, lower.index))
            if key in built_horizontal:

                # A downward door already exists on this seam: upgrade it
                existing = built_horizontal[key]
                existing.arrow_direction = "up_down"
                existing.show_arrow = arrows_on and (upper.arrows or lower.arrows)
                continue
            if named_down:
                continue  # tried above and failed the shared-wall check; already logged, don't double
            shared_c0, shared_c1 = self._get_shared_wall_columns(upper, lower)
            shared = shared_c1 - shared_c0
            if shared < minimum:
                log(
                    f"'{upper.label}' and '{lower.label}' only share {shared} tile(s) of wall, but a "
                    f"doorway needs {minimum}. Widen one of the rooms, or leave them without a doorway."
                )
                continue
            tile_x0 = shared_c0 + (shared - opening) // 2
            tile_x0 = self._adjust_door_opening(tile_x0, shared_c0, shared_c1, axis="horizontal")
            door = Dungeon.Door(
                tile_x0,
                tile_x0 + opening,
                upper.tile_y1,
                arrows_on and lower.arrows,
                axis="horizontal",
                arrow_direction="up",
            )
            self.doors.append(door)
            built_horizontal[key] = door

        # Put a doorway in the wall between each room and every room its {to=...} explicitly names
        vertical_opening = self.DOOR_OPENING_ROWS
        vertical_minimum = self.DOOR_MIN_SHARED_ROWS

        for source, target in self._vertical_door_pairs():

            # source is whichever room's {to=...} produced this pair
            left, right = (source, target) if source.tile_x1 <= target.tile_x0 else (target, source)

            shared_r0, shared_r1 = self._get_shared_wall_rows(left, right)
            shared = shared_r1 - shared_r0
            if shared < vertical_minimum:
                log(
                    f"'{left.label}' and '{right.label}' only share {shared} tile(s) of wall, but a "
                    f"doorway needs {vertical_minimum}. Heighten one of the rooms, or leave them "
                    "without a doorway."
                )
                continue

            mutual = self._is_mutual_door(source, target)
            if mutual:
                arrow_direction = "left_right"
            else:
                arrow_direction = "right" if source is left else "left"
            wants_arrow = (left.arrows or right.arrows) if mutual else source.arrows
            show_arrow = arrows_on and wants_arrow

            # Center the opening on the shared wall, snapped to a whole tile row
            tile_y0 = shared_r0 + (shared - vertical_opening) // 2
            tile_y0 = self._adjust_door_opening(tile_y0, shared_r0, shared_r1, axis="vertical")
            self.doors.append(
                Dungeon.Door(
                    left.tile_x1,
                    0,
                    tile_y0,
                    show_arrow,
                    axis="vertical",
                    tile_y1=tile_y0 + vertical_opening,
                    arrow_direction=arrow_direction,
                )
            )

        # Tell each room which pixel ranges of its walls the doorways clear away
        self._assign_door_gaps()

    def _init_grid_constants(self):
        """
        Set the tile-grid constants (`TILE_SIZE`, `GRID_ORIGIN_X`, `GRID_ORIGIN_Y`,
        `GRID_COLUMNS`, `GRID_ROWS`).
        """

        self.TILE_SIZE = 80
        self.GRID_ORIGIN_X = 110
        self.GRID_ORIGIN_Y = 289
        self.GRID_COLUMNS = 16  # 16 * 80 = 1280 = 1500 - 2 * 110
        self.GRID_ROWS = 19  # 19 * 80 = 1520 ~= 1522

    def _init_wall_constants(self):
        """
        Set the wall/doorway/arrow asset-path and geometry constants (`WALL_PATH`,
        `WALL_TEXTURE_PREFIX`, `ARROW_PATHS`, etc.).
        """

        # Walls
        self.WALL_PATH = "dungeon/regular/wall"
        self.WALL_SHAPE_FOLDER = "shape"
        self.WALL_EFFECT_FOLDER = "effect"
        self.WALL_TEXTURE_PREFIX = "dungeon/regular/wall/texture/"
        self.WALL_OUTER_PIECE = "outer"

        # Doorways
        self.WALL_HORIZONTAL_DOORWAY_PIECE = "horizontal_doorway"
        self.WALL_VERTICAL_DOORWAY_PIECE = "vertical_doorway"
        self.DOOR_OPENING_COLUMNS = 2
        self.DOOR_OPENING_ROWS = 2
        self.DOORWAY_PIECE_WIDTH = 240
        self.DOORWAY_PIECE_HEIGHT = 160
        self.DOOR_MIN_SHARED_COLUMNS = self.DOOR_OPENING_COLUMNS + 2
        self.DOOR_MIN_SHARED_ROWS = self.DOOR_OPENING_ROWS + 2

        # Arrows
        self.ARROW_PATHS = {
            "up": "dungeon/regular/wall/arrow/up",
            "down": "dungeon/regular/wall/arrow/down",
            "left": "dungeon/regular/wall/arrow/left",
            "right": "dungeon/regular/wall/arrow/right",
            "left_right": "dungeon/regular/wall/arrow/left_right",
            "up_down": "dungeon/regular/wall/arrow/up_down",
        }
        self.ARROW_WIDTH = 80
        self.ARROW_HEIGHT = 80
        self.ARROW_OFFSET_Y = 0
        self.ARROW_OFFSET_X = 0

    def _get_dungeon_placeholder_regex(self) -> re.Pattern:
        """
        Return the regex that recognizes dungeon room directives (`{row}`, `{to=...}`, etc.)
        in the rules text.
        """

        return re.compile(
            r"\{\s*(rowspan|row|new-?row|id|span|height|to|doors?|nameless|no-?name|no-?arrows?|arrows?)"
            r"\s*(?:[=:]\s*([^{}]*?))?\s*\}",
            re.IGNORECASE,
        )

    def _stamp_outer_wall(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece):
        """
        Stamp the card's outer wall border (`WALL_OUTER_PIECE`) onto the whole card.

        Parameters
        ----------
        shape : Image
            The "L" silhouette `_create_wall_layers` is building, modified in place.

        effect : Image
            The RGBA effect image `_create_wall_layers` is building, modified in place.

        stamp_wall_piece : function
            `_create_wall_layers`'s own `stamp_wall_piece(shape, effect, name, position, size,
            clip=None, clip_axis_vertical=False)` closure, passed in since it isn't a method.
        """

        stamp_wall_piece(shape, effect, self.WALL_OUTER_PIECE, (0, 0), (self.CARD_WIDTH, self.CARD_HEIGHT))

    def _is_wall_suppressed(
        self, room: "Dungeon.Room", edge: str, column: int | None = None, row: int | None = None
    ) -> bool:
        """
        This is always false for a plain Dungeon. Only relevant in subclasses.

        Parameters
        ----------
        room : Dungeon.Room
            The room whose wall tile is being considered.

        edge : str
            Which edge of the room this tile is on.

        column : int, optional
            The tile column of the specific wall tile being considered, if the caller has one
            (`build_wall_images`'s per-tile loop always passes this).

        row : int, optional
            The tile row of the specific wall tile being considered, if the caller has one.
        """

        return False

    def _stamp_horizontal_doorway(
        self, shape: Image.Image, effect: Image.Image, stamp_wall_piece, door: "Dungeon.Door"
    ):
        """
        Stamp a horizontal doorway's art (`WALL_HORIZONTAL_DOORWAY_PIECE`), centered on the seam,
        at its full size.

        Parameters
        ----------
        shape : Image
            The "L" silhouette `_create_wall_layers` is building, modified in place.

        effect : Image
            The RGBA effect image `_create_wall_layers` is building, modified in place.

        stamp_wall_piece : function
            `_create_wall_layers`'s own `stamp_wall_piece(shape, effect, name, position, size,
            clip=None, clip_axis_vertical=False)` closure, passed in since it isn't a method.

        door : Dungeon.Door
            The horizontal doorway to stamp.
        """

        stamp_wall_piece(
            shape,
            effect,
            self.WALL_HORIZONTAL_DOORWAY_PIECE,
            (
                self._door_center_x(door) - self.DOORWAY_PIECE_WIDTH // 2,
                self._get_seam_y(door) - self.DOORWAY_PIECE_HEIGHT // 2,
            ),
            (self.DOORWAY_PIECE_WIDTH, self.DOORWAY_PIECE_HEIGHT),
        )

    def _stamp_vertical_doorway(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece, door: "Dungeon.Door"):
        """
        Stamp a vertical doorway's art (`WALL_VERTICAL_DOORWAY_PIECE`), centered on the seam, at its
        full size.

        Parameters
        ----------
        shape : Image
            The "L" silhouette `_create_wall_layers` is building, modified in place.

        effect : Image
            The RGBA effect image `_create_wall_layers` is building, modified in place.

        stamp_wall_piece : function
            `_create_wall_layers`'s own `stamp_wall_piece(shape, effect, name, position, size,
            clip=None, clip_axis_vertical=False)` closure, passed in since it isn't a method.

        door : Dungeon.Door
            The vertical doorway to stamp.
        """

        stamp_wall_piece(
            shape,
            effect,
            self.WALL_VERTICAL_DOORWAY_PIECE,
            (
                self._get_seam_x(door) - self.DOORWAY_PIECE_HEIGHT // 2,
                self._door_center_y(door) - self.DOORWAY_PIECE_WIDTH // 2,
            ),
            (self.DOORWAY_PIECE_HEIGHT, self.DOORWAY_PIECE_WIDTH),
        )

    def _parse_door_targets(self, value: str) -> list[str]:
        """
        Parse a `{to=...}` value into a list of target room identifiers
        """

        if value.lower().strip() in ("", "none", "-"):
            return []
        return [part.strip().lower() for part in value.split(",") if part.strip()]

    def create_layers(
        self,
        create_art_layer: bool = True,
        create_frame_layers: bool = True,
        create_watermark_layer: bool = True,
        create_rarity_symbol_layer: bool = True,
        create_footer_layer: bool = True,
        create_mana_cost_layer: bool = True,
        create_title_layer: bool = True,
        create_type_layer: bool = True,
        create_rules_text_layer: bool = True,
        create_power_toughness_layer: bool = True,
        create_overlay_layers: bool = True,
        create_wall_layers: bool = True,
        create_arrow_layers: bool = True,
        create_room_name_layers: bool = True,
    ):
        """
        Append every frame, text, and collector layer to the card based on `self.metadata`.

        Parameters
        ----------
        create_art_layer: bool, default: True
            Whether to put the card's art in or not.

        create_frame_layers: bool, default: True
            Whether to put the card's frames on or not.

        create_watermark_layer: bool, default: True
            Whether to put the watermark on the card or not.

        create_rarity_symbol_layer: bool, default: True
            Whether to put the rarity/set symbol on the card or not.

        create_footer_layer: bool, default: True
            Whether to put the footer collector info on the bottom of the card or not.

        create_mana_cost_layer: bool, default: True
            Whether to put the mana cost of the card on it or not.

        create_title_layer: bool, default: True
            Whether to put the title of the card on it or not.

        create_type_layer: bool, default: True
            Whether to put the type line of the card on it or not.

        create_rules_text_layer: bool, default: True
            Whether to put the rules text of the card on it or not.

        create_power_toughness_layer: bool, default: True
            Whether to put the power & toughness of the card on it or not.

        create_overlay_layers: bool, default: True
            Whether to put the overlays on top of the card after everything else or not.

        create_wall_layers: bool, default: True
            Whether to put the dungeon's walls on it or not.

        create_arrow_layers: bool, default: True
            Whether to put the direction arrows in the doorways or not.

        create_room_name_layers: bool, default: True
            Whether to put each room's name on it or not.
        """

        if create_art_layer:
            self._create_art_layer(log_errors=False)

        super().create_layers(
            False,  # art for dungeons is optional, so don't log if it isn't found
            create_frame_layers,
            create_watermark_layer,
            False,  # dungeons don't have a rarity symbol
            create_footer_layer,
            create_mana_cost_layer,
            create_title_layer,
            create_type_layer,
            create_rules_text_layer,
            False,  # dungeons don't have power & toughness
            create_overlay_layers,
        )

        if create_wall_layers:
            self._create_wall_layers()

        if create_arrow_layers:
            self._create_arrow_layers()

        if create_room_name_layers:
            self._create_room_name_layers()

    def _compute_room_widths(self):
        """
        Give each room a column range that (a) tiles its row across the whole grid with no gaps,
        (b) makes every explicit `{to=...}` doorway's two rooms overlap by at least
        `DOOR_MIN_SHARED_COLUMNS`, and (c) sizes rooms in proportion to their `span`.
        """

        def min_width(room: "Dungeon.Room") -> int:
            return max(room.min_columns, self.MIN_ROOM_COLUMNS)

        # Base proportional layout, top row down
        row_chains: list[list["Dungeon.Room"]] = []
        occupied: dict[int, list[tuple[int, int]]] = {}
        for row_index, row in enumerate(self.rows):
            segments: list[tuple[int, int]] = []
            cursor = 0
            for start, end in sorted(occupied.get(row_index, [])):
                if start > cursor:
                    segments.append((cursor, start))
                cursor = max(cursor, end)
            if cursor < self.GRID_COLUMNS:
                segments.append((cursor, self.GRID_COLUMNS))
            if not segments:
                log(
                    f"Row {row_index + 1} of this dungeon is completely covered by rooms spanning into it."
                    " Its rooms will overlap them."
                )
                segments = [(0, self.GRID_COLUMNS)]

            # Split this row's own rooms across the free segments in reading order, by segment width
            if len(segments) == 1 or len(row) <= 1:
                groups = [list(row)] + [[] for _ in segments[1:]]
            else:
                counts = allocate_by_weight([float(end - start) for start, end in segments], len(row), 0)
                groups, index = [], 0
                for count in counts:
                    groups.append(row[index : index + count])
                    index += count
                if index < len(row):
                    groups[-1] += row[index:]

            # Lay each segment's rooms out to fill it exactly
            for (start, end), rooms in zip(segments, groups):
                if not rooms:
                    continue
                widths = allocate_by_weight([room.span for room in rooms], end - start, [min_width(r) for r in rooms])
                column = start
                for room, width in zip(rooms, widths):
                    room.tile_x0 = column
                    room.tile_x1 = column + width
                    column += width
                    for spanned in range(row_index + 1, row_index + room.rowspan):
                        occupied.setdefault(spanned, []).append((room.tile_x0, room.tile_x1))

            # This row's full left-to-right occupant chain
            occupants = [room for room in self.rooms if room.row <= row_index < room.row + room.rowspan]
            occupants.sort(key=lambda room: room.tile_x0)
            row_chains.append(occupants)

        # Every explicit horizontal doorway (downward or upward), normalized as (upper, lower)
        doorway_pairs: list[tuple["Dungeon.Room", "Dungeon.Room"]] = [
            (upper, lower) for upper, lower, _, _ in self._horizontal_door_pairs()
        ]

        # Difference-constraints system, solved by Bellman-Ford longest path

        LEFT, RIGHT = "O", "T"
        edges: dict[str, list[tuple[str, int]]] = {}

        def add_edge(u: str, v: str, weight: int):
            edges.setdefault(u, []).append((v, weight))

        add_edge(LEFT, RIGHT, self.GRID_COLUMNS)
        add_edge(RIGHT, LEFT, -self.GRID_COLUMNS)
        for room in self.rooms:
            left, right = f"L{room.index}", f"R{room.index}"
            add_edge(LEFT, left, 0)
            add_edge(right, RIGHT, 0)
            add_edge(left, right, max(room.min_columns, self.MIN_ROOM_COLUMNS))
        for chain in row_chains:
            if not chain:
                continue
            add_edge(f"L{chain[0].index}", LEFT, 0)
            add_edge(RIGHT, f"R{chain[-1].index}", 0)
            for previous, room in zip(chain, chain[1:]):
                add_edge(f"R{previous.index}", f"L{room.index}", 0)
                add_edge(f"L{room.index}", f"R{previous.index}", 0)
        for count, (room, other) in enumerate(doorway_pairs):
            witness = f"D{count}"
            add_edge(f"L{room.index}", witness, 0)
            add_edge(f"L{other.index}", witness, 0)
            add_edge(witness, f"R{room.index}", self.DOOR_MIN_SHARED_COLUMNS)
            add_edge(witness, f"R{other.index}", self.DOOR_MIN_SHARED_COLUMNS)

        nodes: set[str] = set(edges)
        for neighbors in edges.values():
            nodes.update(v for v, _ in neighbors)
        distance: dict[str, int] = {node: 0 for node in nodes}
        feasible = True
        for _ in range(len(nodes)):
            changed = False
            for u, neighbors in edges.items():
                for v, weight in neighbors:
                    if distance[u] + weight > distance[v]:
                        distance[v] = distance[u] + weight
                        changed = True
            if not changed:
                break
        else:
            feasible = False
        if feasible:
            feasible = not any(
                distance[u] + weight > distance[v] for u, neighbors in edges.items() for v, weight in neighbors
            )

        if not feasible:
            log(
                "This dungeon's rooms can't all fit their {to=...} doorways, even at every "
                "room's minimum width. Widen the dungeon's rooms, or remove some doorways. Rendering "
                "without doorway-aware layout..."
            )
            return  # the base proportional layout above is already applied and gap-free

        # Doorways may still fall short of their overlap, so fix them
        spanning = {room.index for room in self.rooms if room.rowspan > 1}
        widths: dict[int, int] = {room.index: room.tile_x1 - room.tile_x0 for room in self.rooms}

        def stretches(chain: list["Dungeon.Room"]) -> list[tuple[int, int, list["Dungeon.Room"]]]:
            """
            Split a row's occupant chain at its spanning obstacles into (start, end, rooms)
            stretches the row's own rooms tile between. Obstacles are from already fixed rooms,
            particularly row-spanning ones.
            """

            result: list[tuple[int, int, list["Dungeon.Room"]]] = []
            run: list["Dungeon.Room"] = []
            start = 0
            for room in chain:
                if room.index in spanning:
                    result.append((start, room.tile_x0, run))
                    run = []
                    start = room.tile_x1
                else:
                    run.append(room)
            result.append((start, self.GRID_COLUMNS, run))
            return result

        def place_all():
            for chain in row_chains:
                for start, _, run in stretches(chain):
                    column = start
                    for room in run:
                        room.tile_x0 = column
                        room.tile_x1 = column + widths[room.index]
                        column = room.tile_x1

        # Grow the two rooms of every under-overlapping doorway until they meet
        def grow(room: "Dungeon.Room", amount: int):
            if room.index in spanning:
                return
            stretch = next(run for _, _, run in stretches(row_chains[room.row]) if room in run)
            for _ in range(amount):
                donors = [
                    other for other in stretch if other.index != room.index and widths[other.index] > min_width(other)
                ]
                if not donors:
                    return
                donor = max(donors, key=lambda other: widths[other.index])
                widths[donor.index] -= 1
                widths[room.index] += 1

        for _ in range(self.GRID_COLUMNS * max(len(doorway_pairs), 1)):
            settled = True
            for room, other in doorway_pairs:
                overlap = min(room.tile_x1, other.tile_x1) - max(room.tile_x0, other.tile_x0)
                if overlap < self.DOOR_MIN_SHARED_COLUMNS:
                    settled = False
                    shortfall = self.DOOR_MIN_SHARED_COLUMNS - overlap
                    grow(room, shortfall)
                    grow(other, shortfall)
                    place_all()
            if settled:
                break

    def _adjust_room_widths_for_text(self):
        """
        Refine the base width layout for rooms holding a longer name or more rules text.
        """

        if not self.rooms:
            return

        def min_width(room: "Dungeon.Room") -> int:
            return max(room.min_columns, self.MIN_ROOM_COLUMNS)

        parent: dict = {}

        def find(node):
            parent.setdefault(node, node)
            root = node
            while parent[root] != root:
                root = parent[root]
            while parent[node] != root:
                parent[node], node = root, parent[node]
            return root

        def union(first, second):
            first_root, second_root = find(first), find(second)
            if first_root != second_root:
                parent[first_root] = second_root

        GRID_LEFT, GRID_RIGHT = "grid-left", "grid-right"
        for row_index in range(len(self.rows)):
            occupants = sorted(
                (room for room in self.rooms if room.row <= row_index < room.row + room.rowspan),
                key=lambda room: room.tile_x0,
            )
            if not occupants:
                continue
            union(GRID_LEFT, (occupants[0].index, "L"))
            union((occupants[-1].index, "R"), GRID_RIGHT)
            for left, right in zip(occupants, occupants[1:]):
                union((left.index, "R"), (right.index, "L"))

        seam_of = {(room.index, side): find((room.index, side)) for room in self.rooms for side in ("L", "R")}
        pinned = {find(GRID_LEFT), find(GRID_RIGHT)}

        seam_pos: dict = {}
        grows_seam: dict = {}  # seam -> rooms with a right edge is this seam
        shrinks_seam: dict = {}  # seam -> rooms with a left edge is this seam
        for room in self.rooms:
            left_seam, right_seam = seam_of[(room.index, "L")], seam_of[(room.index, "R")]
            seam_pos[left_seam] = room.tile_x0
            seam_pos[right_seam] = room.tile_x1
            grows_seam.setdefault(right_seam, []).append(room)
            shrinks_seam.setdefault(left_seam, []).append(room)
        movable = [seam for seam in seam_pos if seam not in pinned]

        def width(room: "Dungeon.Room") -> int:
            return seam_pos[seam_of[(room.index, "R")]] - seam_pos[seam_of[(room.index, "L")]]

        def sync_rooms():
            for room in self.rooms:
                room.tile_x0 = seam_pos[seam_of[(room.index, "L")]]
                room.tile_x1 = seam_pos[seam_of[(room.index, "R")]]

        # Protected doorways, with the overlap each one starts at
        # Protected doorways, with the overlap each one starts at: every explicit horizontal pair
        # (downward or upward), plus each automatic room's current downward neighbours
        protected_pairs: list[tuple["Dungeon.Room", "Dungeon.Room"]] = [
            (upper, lower) for upper, lower, _, _ in self._horizontal_door_pairs()
        ]
        for room in self.rooms:
            if room.door_targets is not None:
                continue
            partner_row = room.row + room.rowspan
            if partner_row >= len(self.rows):
                continue
            for other in self.rows[partner_row]:
                overlap = min(room.tile_x1, other.tile_x1) - max(room.tile_x0, other.tile_x0)
                if overlap >= self.DOOR_MIN_SHARED_COLUMNS:
                    protected_pairs.append((room, other))
        baseline_overlaps = [
            min(first.tile_x1, second.tile_x1) - max(first.tile_x0, second.tile_x0) for first, second in protected_pairs
        ]

        def doorways_ok() -> bool:
            for (first, second), baseline in zip(protected_pairs, baseline_overlaps):
                overlap = min(first.tile_x1, second.tile_x1) - max(first.tile_x0, second.tile_x0)
                if overlap < min(baseline, self.DOOR_MIN_SHARED_COLUMNS):
                    return False
            return True

        def text_weight(room: "Dungeon.Room") -> float:
            content_width = max((room.tile_x1 - room.tile_x0) * self.TILE_SIZE - 2 * self.ROOM_CONTENT_INSET_X, 1)
            natural_height = self._measure_room_content(room, self.ROOM_TEXT_MAX_FONT_SIZE, content_width)["height"]
            if natural_height == float("inf"):
                natural_height = self.RULES_BOX_HEIGHT
            return max(natural_height * content_width, 0.01)

        def name_columns(room: "Dungeon.Room") -> int:
            """
            Columns a room needs so its single-line name fits without shrinking.
            """

            if not room.name:
                return 0
            size = min(
                max(int(round(self.ROOM_TEXT_MAX_FONT_SIZE * self.ROOM_NAME_FONT_SCALE)), self.ROOM_NAME_MIN_FONT_SIZE),
                self.ROOM_NAME_MAX_FONT_SIZE,
            )
            font = load_font(self.ROOM_NAME_FONT, size)
            fallback_fonts = self._load_fallback_fonts(self.ROOM_NAME_FONT, size)
            name_width = int(self._get_ucs_chunks_length(self._get_room_name_text(room), font, fallback_fonts))

            # Match the margins _measure_room_content leaves around the name inside the room
            body_margin = int(max(self.ROOM_TEXT_MAX_FONT_SIZE, 1) * 0.25)

            needed = name_width + 2 * body_margin + 2 * self.ROOM_CONTENT_INSET_X
            return min((needed + self.TILE_SIZE - 1) // self.TILE_SIZE, self.GRID_COLUMNS)

        weight_of = {room.index: text_weight(room) for room in self.rooms}
        name_of = {room.index: name_columns(room) for room in self.rooms}
        target_samples: dict = {room.index: [] for room in self.rooms}
        for row_index in range(len(self.rows)):
            occupants = sorted(
                (room for room in self.rooms if room.row <= row_index < room.row + room.rowspan),
                key=lambda room: room.tile_x0,
            )
            if not occupants:
                continue
            allocation = allocate_by_weight(
                [weight_of[room.index] for room in occupants],
                self.GRID_COLUMNS,
                [min_width(room) for room in occupants],
            )
            for room, value in zip(occupants, allocation):
                target_samples[room.index].append(value)
        target_of = {
            index: max(
                (sum(samples) / len(samples) if samples else 0.0),
                float(name_of[index]),
            )
            for index, samples in target_samples.items()
        }

        def move_delta_cost(seam, delta: int) -> float:
            cost = 0.0
            for room in grows_seam.get(seam, []):  # right edge
                deviation = width(room) - target_of[room.index]
                cost += (deviation + delta) ** 2 - deviation**2
            for room in shrinks_seam.get(seam, []):  # left edge
                deviation = width(room) - target_of[room.index]
                cost += (deviation - delta) ** 2 - deviation**2
            return cost

        for _ in range(self.GRID_COLUMNS * max(len(self.rooms), 1) * 4):
            best_seam, best_delta, best_cost = None, 0, -1e-9
            for seam in movable:
                for delta in (1, -1):
                    shrinking = shrinks_seam.get(seam, []) if delta > 0 else grows_seam.get(seam, [])
                    if any(width(room) - 1 < min_width(room) for room in shrinking):
                        continue
                    cost = move_delta_cost(seam, delta)
                    if cost >= best_cost:
                        continue
                    seam_pos[seam] += delta
                    sync_rooms()
                    feasible = doorways_ok()
                    seam_pos[seam] -= delta
                    sync_rooms()
                    if feasible:
                        best_seam, best_delta, best_cost = seam, delta, cost
            if best_seam is None:
                break
            seam_pos[best_seam] += best_delta
            sync_rooms()

        sync_rooms()

    def _compute_row_heights(self):
        """
        Size each row purely from how much text its rooms hold, then make sure every room that spans
        several rows fits across them, then snap the whole column of rows to whole tiles.
        """

        def measure_room_natural_height(room: "Dungeon.Room") -> float:
            """
            Return the height a room's contents want, at the maximum font size, in its own width.
            """

            content_width = max((room.tile_x1 - room.tile_x0) * self.TILE_SIZE - 2 * self.ROOM_CONTENT_INSET_X, 1)
            metrics = self._measure_room_content(room, self.ROOM_TEXT_MAX_FONT_SIZE, content_width)
            return metrics["height"] + 2 * self.ROOM_CONTENT_INSET_Y

        count = len(self.rows)
        naturals = [0.0] * count
        spanning: list[tuple["Dungeon.Room", float]] = []

        for room in self.rooms:
            natural = measure_room_natural_height(room)
            if room.rowspan <= 1:
                naturals[room.row] = max(naturals[room.row], natural)
            else:
                spanning.append((room, natural))

        # Rows that hold nothing but rooms spanning through them get seeded from those rooms
        for room, natural in spanning:
            share = natural / room.rowspan
            for index in range(room.row, room.row + room.rowspan):
                if naturals[index] <= 0:
                    naturals[index] = share
        for index in range(count):
            if naturals[index] <= 0:
                naturals[index] = 1.0

        # Grow rows until each spanning room fits across the rows it covers
        for room, natural in sorted(spanning, key=lambda pair: pair[0].rowspan):
            rows = list(range(room.row, room.row + room.rowspan))
            current = sum(naturals[index] for index in rows)
            if current >= natural:
                continue
            deficit = natural - current
            for index in rows:
                share = (naturals[index] / current) if current > 0 else (1 / len(rows))
                naturals[index] += deficit * share

        weights: list[float] = []
        for index, natural in enumerate(naturals):
            multiplier = next(
                (room.pixel_height_multiplier for room in self.rows[index] if room.pixel_height_multiplier is not None),
                1.0,
            )
            weights.append(max(natural * multiplier, 0.01))

        # Rows touched by a vertical doorway need enough combined height to fit it
        minimums = [self.MIN_ROW_TILES] * count
        for start, end in self._vertical_door_pair_rows:
            span = max(end - start, 1)
            share = -(-self.DOOR_MIN_SHARED_ROWS // span)
            for index in range(start, end):
                minimums[index] = max(minimums[index], share)

        self._row_tile_heights = allocate_by_weight(weights, self.GRID_ROWS, minimums)

    def _finalize_room_rects(self):
        """
        Turn the tile heights into grid rows (spanning rooms reach the bottom of their last row) and
        pixel rectangles.
        """

        row_tops: list[int] = []
        tile_row = 0
        for height in self._row_tile_heights:
            row_tops.append(tile_row)
            tile_row += height
        row_tops.append(tile_row)

        for room in self.rooms:
            room.tile_y0 = row_tops[room.row]
            room.tile_y1 = row_tops[min(room.row + room.rowspan, len(self.rows))]
            room.pixel_x = self.GRID_ORIGIN_X + room.tile_x0 * self.TILE_SIZE
            room.pixel_y = self.GRID_ORIGIN_Y + room.tile_y0 * self.TILE_SIZE
            room.pixel_width = (room.tile_x1 - room.tile_x0) * self.TILE_SIZE
            room.pixel_height = (room.tile_y1 - room.tile_y0) * self.TILE_SIZE

    def _shared_wall_width(self, first: "Dungeon.Room", second: "Dungeon.Room") -> int:
        """
        Return how many tile columns of wall two rooms share (0 if they don't overlap horizontally).
        """

        low, high = self._get_shared_wall_columns(first, second)
        return max(high - low, 0)

    def _shared_wall_height(self, first: "Dungeon.Room", second: "Dungeon.Room") -> int:
        """
        Return how many tile rows of wall two rooms share (0 if they don't overlap vertically).
        """

        low, high = self._get_shared_wall_rows(first, second)
        return max(high - low, 0)

    def _is_below(self, room: "Dungeon.Room", other: "Dungeon.Room") -> bool:
        """
        Return whether `other` is directly below `room` (its top row-band starts where `room`'s
        row-band ends), the relationship a horizontal doorway connects.
        """

        return other.row == room.row + room.rowspan

    def _is_beside(self, room: "Dungeon.Room", other: "Dungeon.Room") -> bool:
        """
        Return whether `other` shares at least one row with `room` without either being directly
        below the other (for a vertical doorway).
        """

        if self._is_below(room, other) or self._is_below(other, room):
            return False
        return room.row < other.row + other.rowspan and other.row < room.row + room.rowspan

    def _vertical_door_pairs(self) -> list[tuple["Dungeon.Room", "Dungeon.Room"]]:
        """
        Return every (room, other) pair connected by an explicit `{to=...}` vertical doorway.
        """

        pairs: list[tuple["Dungeon.Room", "Dungeon.Room"]] = []
        seen: set[frozenset] = set()
        for room in self.rooms:
            if room.door_targets is None:
                continue
            for identifier in room.door_targets:
                other = self.room_ids.get(identifier)
                if other is None or other is room or not self._is_beside(room, other):
                    continue
                key = frozenset((room.index, other.index))
                if key in seen:
                    continue
                seen.add(key)
                pairs.append((room, other))
        return pairs

    def _horizontal_door_pairs(self) -> list[tuple["Dungeon.Room", "Dungeon.Room", bool, bool]]:
        """
        Return every explicit `{to=...}` horizontal doorway as a normalized
        `(upper, lower, named_down, named_up)` tuple.
        """

        pairs: dict[frozenset, list] = {}
        order: list[frozenset] = []
        for room in self.rooms:
            if room.door_targets is None:
                continue
            for identifier in room.door_targets:
                other = self.room_ids.get(identifier)
                if other is None or other is room:
                    continue
                if self._is_below(room, other):
                    upper, lower, named_down, named_up = room, other, True, False
                elif self._is_below(other, room):
                    upper, lower, named_down, named_up = other, room, False, True
                else:
                    continue
                key = frozenset((upper.index, lower.index))
                if key not in pairs:
                    pairs[key] = [upper, lower, named_down, named_up]
                    order.append(key)
                else:
                    pairs[key][2] = pairs[key][2] or named_down
                    pairs[key][3] = pairs[key][3] or named_up
        return [tuple(pairs[key]) for key in order]

    def _assign_door_gaps(self):
        """
        Tell each room which pixel ranges of its walls the doorways clear away. Broken out of
        `__init__` so a subclass that post-processes door positions after construction (e.g.
        `ExpandedDungeonGlobal`'s seam-snapping) can recompute the gaps from the adjusted positions.
        """

        for room in self.rooms:
            room.top_pixel_gaps = []
            room.bottom_pixel_gaps = []
            room.left_pixel_gaps = []
            room.right_pixel_gaps = []
        for door in self.doors:
            if door.axis == "horizontal":
                gap = (self._door_start_x(door), self._door_end_x(door))
                for room in self.rooms:
                    if room.tile_y1 == door.tile_y:
                        room.bottom_pixel_gaps.append(gap)
                    elif room.tile_y0 == door.tile_y:
                        room.top_pixel_gaps.append(gap)
            else:
                gap = (self._door_start_y(door), self._door_end_y(door))
                for room in self.rooms:
                    if room.tile_x1 == door.tile_x0:
                        room.right_pixel_gaps.append(gap)
                    elif room.tile_x0 == door.tile_x0:
                        room.left_pixel_gaps.append(gap)

    def _adjust_door_opening(
        self, tile_start: int, shared_start: int, shared_end: int, axis: str = "horizontal"
    ) -> int:
        """
        Adjusts door opening across card borders. Not relevant for plain Dungeon, since it's
        all contained within a single card.

        Parameters
        ----------
        tile_start : int
            The centered first tile (column for a horizontal doorway, row for a vertical one) of
            the opening.

        shared_start : int
            The first tile of the wall the two rooms share.

        shared_end : int
            The tile just past the shared wall (exclusive end).

        axis : str, default: "horizontal"
            Which kind of doorway is being placed.
        """

        return tile_start

    def _room_names(self, source: "Dungeon.Room", target: "Dungeon.Room", target_card: "Dungeon" = None) -> bool:
        """
        Return whether `source`'s own `{to=...}` explicitly names `target`.

        Parameters
        ----------
        source : Dungeon.Room
            The room whose `{to=...}` is being checked.

        target : Dungeon.Room
            The room `source` might name.

        target_card : Dungeon, optional
            Irrelevant for plain Dungeons (all the rooms are on one card).
        """

        return source.door_targets is not None and any(
            self.room_ids.get(identifier) is target for identifier in source.door_targets
        )

    def _is_mutual_door(self, room: "Dungeon.Room", other: "Dungeon.Room", other_card: "Dungeon" = None) -> bool:
        """
        Return whether `room` and `other` each explicitly name the other in their own `{to=...}`.

        Parameters
        ----------
        room : Dungeon.Room
            One of the two rooms, on this card.

        other : Dungeon.Room
            The other room. On this same card for a plain `Dungeon`; possibly on a different card
            for a subclass like `ExpandedDungeonLocal` (see `other_card`).

        other_card : Dungeon, optional
            Irrelevant for base Dungeons, since it's all on one card.
        """

        other_self = self if other_card is None else other_card
        return self._room_names(room, other, other_card) and other_self._room_names(other, room, self)

    def _door_targets_for(
        self, room: "Dungeon.Room", min_overlap: int | None = None, log_problems: bool = False
    ) -> list["Dungeon.Room"]:
        """
        Return the rooms directly below `room` that it should have a horizontal doorway to.

        Parameters
        ----------
        room : Dungeon.Room
            The room whose downward doorways are wanted.

        min_overlap : int, optional
            How many tiles an automatic neighbour must overlap to count. Defaults to
            `DOOR_MIN_SHARED_COLUMNS` (a placeable door).

        log_problems : bool, default: False
            Whether to log explicit targets that name an unknown room or one that isn't directly
            below, above, or beside it.
        """

        if min_overlap is None:
            min_overlap = self.DOOR_MIN_SHARED_COLUMNS

        if room.door_targets is None:
            return [
                other
                for other in self.rooms
                if other is not room
                and other.tile_y0 == room.tile_y1
                and self._shared_wall_width(room, other) >= min_overlap
            ]

        targets: list["Dungeon.Room"] = []
        for identifier in room.door_targets:
            other = self.room_ids.get(identifier)
            if other is None:
                if log_problems:
                    log(f"'{room.label}' has a doorway to '{identifier}', which isn't a room in this dungeon.")
                continue
            if self._is_beside(room, other):
                continue  # handled by _vertical_door_targets_for
            if self._is_below(other, room):
                continue  # an upward doorway; handled by _horizontal_door_pairs
            if not self._is_below(room, other):
                if log_problems:
                    log(
                        f"'{room.label}' has a doorway to '{other.label}', which isn't directly "
                        "below, above, or beside it."
                    )
                continue
            targets.append(other)
        return targets

    def _vertical_door_targets_for(self, room: "Dungeon.Room", log_problems: bool = False) -> list["Dungeon.Room"]:
        """
        Return the rooms beside `room` that it should have a vertical doorway to.
        Vertical doorways are never automatic, unlike horizontal ones.

        Parameters
        ----------
        room : Dungeon.Room
            The room whose sideways doorways are wanted.

        log_problems : bool, default: False
            Whether to log explicit targets that name an unknown room.
        """

        if room.door_targets is None:
            return []

        targets: list["Dungeon.Room"] = []
        for identifier in room.door_targets:
            other = self.room_ids.get(identifier)
            if other is None:
                if log_problems:
                    log(f"'{room.label}' has a doorway to '{identifier}', which isn't a room in this dungeon.")
                continue
            if not self._is_beside(room, other):
                continue  # handled by _door_targets_for instead
            targets.append(other)
        return targets

    def _get_shared_wall_columns(self, first: "Dungeon.Room", second: "Dungeon.Room") -> tuple[int, int]:
        """
        Return the tile-column range of wall two rooms share: between the closest of their two left
        walls and the closest of their two right walls, as (start_column, end_column) exclusive.
        """

        low = max(first.tile_x0, second.tile_x0)
        high = min(first.tile_x1, second.tile_x1)
        return low, high

    def _get_shared_wall_rows(self, first: "Dungeon.Room", second: "Dungeon.Room") -> tuple[int, int]:
        """
        Return the tile-row range of wall two rooms share: between the closest of their two top
        walls and the closest of their two bottom walls, as (start_row, end_row) exclusive.
        """

        low = max(first.tile_y0, second.tile_y0)
        high = min(first.tile_y1, second.tile_y1)
        return low, high

    def _door_start_x(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel x where a horizontal doorway's opening begins.
        """

        return self.GRID_ORIGIN_X + door.tile_x0 * self.TILE_SIZE

    def _door_end_x(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel x where a horizontal doorway's opening ends.
        """

        return self.GRID_ORIGIN_X + door.tile_x1 * self.TILE_SIZE

    def _door_start_y(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel y where a vertical doorway's opening begins.
        """

        return self.GRID_ORIGIN_Y + door.tile_y * self.TILE_SIZE

    def _door_end_y(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel y where a vertical doorway's opening ends.
        """

        return self.GRID_ORIGIN_Y + door.tile_y1 * self.TILE_SIZE

    def _get_room_body_text(self, room: "Dungeon.Room", centered: bool | None = None) -> str:
        """
        Return a room's rules text, normalized to a single canonical `{center}` (or none at all).
        """

        if centered is None:
            centered = self.ROOM_TEXT_CENTERED or bool(re.search(r"\{center\}", room.body, re.IGNORECASE))
        text = re.sub(r"\{center\}", "", room.body, flags=re.IGNORECASE)
        return f"{text}{{center}}" if centered else text

    def _get_room_name_text(self, room: "Dungeon.Room") -> str:
        """
        Parse the room name out of the text of a room.
        """

        return replace_ticks(self._replace_text_placeholders(room.name)).replace("\n", " ").strip()

    def _measure_room_content(self, room: "Dungeon.Room", body_size: int, content_width: int) -> dict:
        """
        Work out how a room's name and rules text lay out at a given rules text font size, including
        whether they fit on one line together.

        Parameters
        ----------
        room : Dungeon.Room
            The room to measure.

        body_size : int
            The font size to measure the room's rules text at.

        content_width : int
            The width available to the room's text.

        Returns
        -------
        dict
            name_size / name_width / name_ascent / name_descent, body_ascent / body_descent,
            inline, separator_width, body_width, content_height, margin, and the total height the
            room's text needs.
        """

        def fit_room_name(name: str, max_width: int, target_size: float) -> tuple[int, int, int, int]:
            """
            Shrink a room name from `target_size` until it fits `max_width`.

            Returns
            -------
            tuple[int, int, int, int]
                The font size, the name's width, and the font's ascent and descent.
            """

            size = min(
                max(int(round(target_size)), self.ROOM_NAME_MIN_FONT_SIZE),
                self.ROOM_NAME_MAX_FONT_SIZE,
            )
            while True:
                font = load_font(self.ROOM_NAME_FONT, size)
                fallback_fonts = self._load_fallback_fonts(self.ROOM_NAME_FONT, size)
                width = self._get_ucs_chunks_length(name, font, fallback_fonts)
                if width <= max_width or size <= self.ROOM_NAME_MIN_FONT_SIZE:
                    break
                size -= 1
            ascent, descent = font.getmetrics()
            return size, int(width), ascent, descent

        def get_laid_out_line_width(line: list[tuple], font_size: int) -> int:
            """
            Measure one laid-out line of rules text, the same way `_create_rules_text_layer`
            measures a line when centering it.
            """

            width = 0.0
            for fragment in line:
                if len(fragment) < 3:
                    continue
                kind, value, fragment_font = fragment[:3]
                if kind in ("text", "dice"):
                    if value:
                        width += self._get_rules_text_fragment_length(value, fragment_font)
                elif kind == "symbol":
                    symbol_width, _, _ = self._get_symbol_metrics(value, fragment_font, font_size)
                    width += symbol_width + self.RULES_TEXT_MANA_SYMBOL_SPACING
            return int(width)

        def measure_body(room: "Dungeon.Room", font_size: int, width: float) -> tuple[int, int, int, int] | None:
            """
            Lay a room's rules text out at exactly `font_size` in the given width, with unlimited
            height, without drawing anything.

            Parameters
            ----------
            room : Dungeon.Room
                The room whose rules text should be measured.

            font_size : int
                The font size to force.

            width : float
                The width to wrap in. Pass `float("inf")` for no wrapping at all.

            Returns
            -------
            tuple[int, int, int, int] | None
                (content height, margin, line count, width of the first line), or None if the text
                couldn't be laid out at all.
            """

            key = (room.index, font_size, width)
            if key in self._body_measurement_cache:
                return self._body_measurement_cache[key]

            previous = (
                self.RULES_TEXT_MAX_FONT_SIZE,
                self.RULES_TEXT_MIN_FONT_SIZE,
                self.RULES_TEXT_WIDTH,
                self.RULES_TEXT_HEIGHT,
                self.get_metadata(CARD_RULES_TEXT),
            )

            self.RULES_TEXT_MAX_FONT_SIZE = max(font_size, 1)
            self.RULES_TEXT_MIN_FONT_SIZE = max(font_size, 1)
            self.RULES_TEXT_WIDTH = width if width == float("inf") else max(int(width), 1)
            self.RULES_TEXT_HEIGHT = float("inf")
            text = self._get_room_body_text(room)
            self.set_metadata(CARD_RULES_TEXT, text)

            result: tuple[int, int, int, int] = None
            try:
                blocks, size, margin, content_height, _ = self._get_rules_text_layout(text)
                line_count = 0
                first_line_width = 0
                for block in blocks:
                    for line in block:
                        if line and line[0][0] == "newline":
                            continue
                        if line_count == 0:
                            first_line_width = get_laid_out_line_width(line, size)
                        line_count += 1
                if len(blocks) > 1:
                    line_count = max(line_count, 2)
                result = (content_height, margin, max(line_count, 1), first_line_width)
            except ValueError:
                result = None
            finally:
                (
                    self.RULES_TEXT_MAX_FONT_SIZE,
                    self.RULES_TEXT_MIN_FONT_SIZE,
                    self.RULES_TEXT_WIDTH,
                    self.RULES_TEXT_HEIGHT,
                ) = previous[:4]
                self.set_metadata(CARD_RULES_TEXT, previous[4])

            self._body_measurement_cache[key] = result
            return result

        metrics = {
            "name_size": 0,
            "name_width": 0,
            "name_ascent": 0,
            "name_descent": 0,
            "body_ascent": 0,
            "body_descent": 0,
            "inline": False,
            "separator_width": 0,
            "body_width": 0,
            "content_height": 0,
            "margin": 0,
            "height": 0,
        }

        if room.name:

            # Make the name match the rules text margining
            body_margin = int(max(body_size, 1) * 0.25)

            name_width_limit = max(content_width - 2 * body_margin, 1)
            size, width, ascent, descent = fit_room_name(
                self._get_room_name_text(room), name_width_limit, body_size * self.ROOM_NAME_FONT_SCALE
            )
            metrics.update(name_size=size, name_width=width, name_ascent=ascent, name_descent=descent)
        name_height = metrics["name_ascent"] + metrics["name_descent"]

        if not room.body:
            metrics["height"] = name_height
            return metrics

        body_font = load_font(self.RULES_TEXT_FONT, max(body_size, 1))
        body_ascent, body_descent = body_font.getmetrics()
        metrics.update(body_ascent=body_ascent, body_descent=body_descent)

        # Check if the rules text is short enough for it and the name to share a line
        if room.name:
            single = measure_body(room, body_size, float("inf"))
            if single is not None and single[2] == 1:
                separator = int(
                    self._get_rules_text_fragment_length(" " * self.ROOM_INLINE_SEPARATOR_SPACES, body_font)
                )
                if metrics["name_width"] + separator + single[3] <= content_width:
                    metrics.update(
                        inline=True,
                        separator_width=separator,
                        body_width=single[3],
                        content_height=single[0],
                        margin=single[1],
                        height=max(metrics["name_ascent"], body_ascent) + max(metrics["name_descent"], body_descent),
                    )
                    return metrics

        wrapped = measure_body(room, body_size, content_width)
        if wrapped is None:
            metrics["height"] = float("inf")
            return metrics

        metrics.update(content_height=wrapped[0], margin=wrapped[1])
        metrics["height"] = name_height + (self.ROOM_NAME_GAP if room.name else 0) + wrapped[0] + 2 * wrapped[1]
        return metrics

    def _create_frame_layers(self):
        """
        Append frame layers, keeping the wall textures out of the base class's hands.
        """

        full = self.get_metadata(CARD_FRAMES)

        self.set_metadata(CARD_FRAMES, self.non_wall_frames)
        super()._create_frame_layers()

        self.set_metadata(CARD_FRAMES, full)

    def _create_wall_texture_image(self) -> Image.Image | None:
        """
        Composite the wall textures listed in the frames column (with their masks) into one
        card-sized image. Return None if none were listed.
        """

        if not self.wall_texture_frames:
            return None

        canvas = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        found = False

        for path, mask_paths in self.wall_texture_frames:
            texture = open_image(f"{FRAMES_PATH}/{path}.png")
            if texture is None:
                log(f"Could not find the dungeon wall texture at '{FRAMES_PATH}/{path}.png'.")
                continue
            texture = texture.convert("RGBA")

            if mask_paths:
                combined = Image.new("L", texture.size, 255)
                for mask_path in mask_paths:
                    mask = open_image(f"{FRAMES_PATH}/{mask_path}.png")
                    if mask is None:
                        log(f"Invalid frame path '{mask_path}'.")
                        continue
                    combined = ImageChops.multiply(combined, mask.convert("RGBA").getchannel("A").resize(texture.size))
                texture = apply_alpha_mask(texture, combined)

            canvas = paste_image(texture, canvas, (0, 0))
            found = True

        return canvas if found else None

    def _create_wall_layers(self):
        """
        Build the dungeon's walls from the wall pieces, mask the wall texture onto them, and append
        the result to `self.frame_layers`.
        """

        def open_wall_piece(folder: str, name: str, size: tuple[int, int]) -> Image.Image | None:
            """
            Open (and cache) a wall piece at the size it's expected to be.
            """

            key = f"{folder}/{name}@{size[0]}x{size[1]}"
            if key in self._wall_piece_cache:
                return self._wall_piece_cache[key]

            path = f"{self.WALL_PATH}/{folder}/{name}"
            piece = open_image(f"{FRAMES_PATH}/{path}.png")
            if piece is None:
                log(f"Could not find the dungeon wall piece at '{FRAMES_PATH}/{path}.png'.")
            else:
                piece = piece.convert("RGBA")
                if piece.size != size:
                    piece = piece.resize(size)
            self._wall_piece_cache[key] = piece
            return piece

        def stamp_wall_piece(
            shape: Image.Image,
            effect: Image.Image,
            name: str,
            position: tuple[int, int],
            size: tuple[int, int],
            clip: tuple[int, int] = None,
            clip_axis_vertical: bool = False,
        ):
            """
            Stamp a wall piece into the silhouette and the effect image.

            Parameters
            ----------
            shape : Image
                The "L" silhouette, modified in place.

            effect : Image
                The RGBA effect image, modified in place.

            name : str
                The piece to stamp, e.g. "top_left", found in the shape and effect folders.

            position : tuple[int, int]
                Where the piece's top left corner goes.

            size : tuple[int, int]
                The size the piece is expected to be.

            clip : tuple[int, int], optional
                An absolute range to crop the piece down to, along x by default (a horizontal wall
                tile clipped by a doorway gap) or along y when `clip_axis_vertical` is set (a
                vertical wall tile clipped by a doorway gap). The piece's art stays exactly where
                it would have been; it's only cut off, never moved or squashed.

            clip_axis_vertical : bool, default: False
                Whether `clip` is a (y_start, y_end) range instead of (x_start, x_end).
            """

            left, top = position
            crop = None
            if clip is not None:
                if clip_axis_vertical:
                    start = max(clip[0] - top, 0)
                    end = min(clip[1] - top, size[1])
                    if end <= start:
                        return
                    crop = (0, start, size[0], end)
                    top += start
                else:
                    start = max(clip[0] - left, 0)
                    end = min(clip[1] - left, size[0])
                    if end <= start:
                        return
                    crop = (start, 0, end, size[1])
                    left += start

            shape_piece = open_wall_piece(self.WALL_SHAPE_FOLDER, name, size)
            if shape_piece is not None:
                alpha = shape_piece.getchannel("A")
                union_alpha_channel(shape, alpha.crop(crop) if crop else alpha, (left, top))

            effect_piece = open_wall_piece(self.WALL_EFFECT_FOLDER, name, size)
            if effect_piece is not None:
                alpha_composite_clipped(effect, effect_piece.crop(crop) if crop else effect_piece, (left, top))

        def build_wall_images() -> tuple[Image.Image, Image.Image]:
            """
            Stamp the outer wall, then every room's border tiles, then the doorway pieces on top.

            Returns
            -------
            tuple[Image, Image]
                The wall silhouette ("L", masks the texture) and the assembled wall effect (RGBA).
            """

            shape = Image.new("L", (self.CARD_WIDTH, self.CARD_HEIGHT), 0)
            effect = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
            tile = (self.TILE_SIZE, self.TILE_SIZE)

            self._stamp_outer_wall(shape, effect, stamp_wall_piece)

            for room in self.rooms:
                for column in range(room.tile_x0, room.tile_x1):
                    for row in range(room.tile_y0, room.tile_y1):
                        is_top = row == room.tile_y0
                        is_bottom = row == room.tile_y1 - 1
                        is_left = column == room.tile_x0
                        is_right = column == room.tile_x1 - 1

                        if not (is_top or is_bottom or is_left or is_right):
                            continue

                        if (
                            is_top
                            and not (is_left or is_right)
                            and self._is_wall_suppressed(room, "top", column=column, row=row)
                        ):
                            continue
                        if (
                            is_bottom
                            and not (is_left or is_right)
                            and self._is_wall_suppressed(room, "bottom", column=column, row=row)
                        ):
                            continue
                        if (
                            is_left
                            and not (is_top or is_bottom)
                            and self._is_wall_suppressed(room, "left", column=column, row=row)
                        ):
                            continue
                        if (
                            is_right
                            and not (is_top or is_bottom)
                            and self._is_wall_suppressed(room, "right", column=column, row=row)
                        ):
                            continue

                        x = self.GRID_ORIGIN_X + column * self.TILE_SIZE
                        y = self.GRID_ORIGIN_Y + row * self.TILE_SIZE

                        if is_top and is_left:
                            name = "top_left"
                        elif is_top and is_right:
                            name = "top_right"
                        elif is_bottom and is_left:
                            name = "bottom_left"
                        elif is_bottom and is_right:
                            name = "bottom_right"
                        elif is_top:
                            name = "top"
                        elif is_bottom:
                            name = "bottom"
                        elif is_left:
                            name = "left"
                        else:
                            name = "right"

                        is_vertical_wall = (is_left or is_right) and not (is_top or is_bottom)
                        if is_vertical_wall:
                            gaps = room.left_pixel_gaps if is_left else room.right_pixel_gaps
                            span = (y, y + self.TILE_SIZE)
                        else:
                            gaps = room.top_pixel_gaps if is_top else (room.bottom_pixel_gaps if is_bottom else [])
                            span = (x, x + self.TILE_SIZE)

                        visible = subtract_intervals(span[0], span[1], gaps)

                        if not visible:
                            if not is_vertical_wall:
                                if is_left:
                                    stamp_wall_piece(shape, effect, "left", (x, y), tile)
                                elif is_right:
                                    stamp_wall_piece(shape, effect, "right", (x, y), tile)
                            continue

                        for start, end in visible:
                            clip = None if (start, end) == span else (start, end)
                            stamp_wall_piece(
                                shape, effect, name, (x, y), tile, clip, clip_axis_vertical=is_vertical_wall
                            )

            # The doorway pieces go in last on top of the full-length wall
            for door in self.doors:
                if door.axis == "horizontal":
                    self._stamp_horizontal_doorway(shape, effect, stamp_wall_piece, door)
                else:
                    self._stamp_vertical_doorway(shape, effect, stamp_wall_piece, door)

            return shape, effect

        if not self.rooms:
            return

        shape, effect = build_wall_images()
        texture = self._create_wall_texture_image()

        if texture is not None:
            wall = apply_alpha_mask(texture, shape)
        else:
            wall = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))

        self.frame_layers.append(Layer(Image.alpha_composite(wall, effect)))

    def _get_seam_y(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel y centerline of the horizontal wall a doorway is in.
        """

        return self.GRID_ORIGIN_Y + door.tile_y * self.TILE_SIZE

    def _get_seam_x(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel x centerline of the vertical wall a doorway is in.
        """

        return self.GRID_ORIGIN_X + door.tile_x0 * self.TILE_SIZE

    def _door_center_x(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel x of the middle of a horizontal doorway's opening.
        """

        return (self._door_start_x(door) + self._door_end_x(door)) // 2

    def _door_center_y(self, door: "Dungeon.Door") -> int:
        """
        Return the pixel y of the middle of a vertical doorway's opening.
        """

        return (self._door_start_y(door) + self._door_end_y(door)) // 2

    def _create_arrow_layers(self):
        """
        Put a direction arrow in the middle of each doorway and append it to `self.frame_layers`.
        """

        if not any(door.show_arrow for door in self.doors):
            return

        arrows: dict[str, Image.Image] = {}
        for direction, path in self.ARROW_PATHS.items():
            arrow = open_image(f"{FRAMES_PATH}/{path}.png")
            if arrow is None:
                log(f"Could not find the dungeon arrow at '{FRAMES_PATH}/{path}.png'.")
                continue
            arrows[direction] = arrow.convert("RGBA").resize((max(self.ARROW_WIDTH, 1), max(self.ARROW_HEIGHT, 1)))

        image = Image.new("RGBA", (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        for door in self.doors:
            if not door.show_arrow:
                continue
            arrow = arrows.get(door.arrow_direction)
            if arrow is None:
                continue
            if door.axis == "horizontal":
                position = (
                    self._door_center_x(door) - arrow.width // 2,
                    self._get_seam_y(door) + self.ARROW_OFFSET_Y - arrow.height // 2,
                )
            else:
                position = (
                    self._get_seam_x(door) + self.ARROW_OFFSET_X - arrow.width // 2,
                    self._door_center_y(door) - arrow.height // 2,
                )
            alpha_composite_clipped(image, arrow, position)
        self.frame_layers.append(Layer(image))

    def _create_room_name_layers(self):
        """
        Draw each room's name and append it to `self.text_layers`.
        """

        for room in self.rooms:
            if not room.name:
                continue
            x, y, width, height = room.name_pixel_box
            if width < 1 or height < 1:
                continue

            name = self._get_room_name_text(room)
            size = max(room.name_font_size, 1)
            font = load_font(self.ROOM_NAME_FONT, size)
            fallback_fonts = self._load_fallback_fonts(self.ROOM_NAME_FONT, size)

            image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            length = self._get_ucs_chunks_length(name, font, fallback_fonts)
            x_pos = (width - length) // 2 if self.ROOM_TEXT_CENTERED else 0

            self._draw_ucs_chunks(
                draw,
                (x_pos, 0),
                name,
                font,
                fallback_fonts,
                primary_font_path=self.ROOM_NAME_FONT,
                font_size=size,
                fill=self.ROOM_NAME_FONT_COLOR,
                stroke_width=self.ROOM_NAME_OUTLINE_SIZE,
                stroke_fill="black",
            )

            self.text_layers.append(Layer(add_drop_shadow(image, self.ROOM_NAME_DROP_SHADOW_OFFSET), (x, y)))

    def _create_rules_text_layer(self):
        """
        Process the rules text of each room and append it to `self.text_layers`. The font size is
        forced to the one the layout was measured with, so drawing can't disagree with measurement.
        """

        full_text = self.get_metadata(CARD_RULES_TEXT)
        if not full_text or "{skip}" in full_text:
            return

        saved = (
            self.RULES_TEXT_X,
            self.RULES_TEXT_Y,
            self.RULES_TEXT_WIDTH,
            self.RULES_TEXT_HEIGHT,
            self.RULES_TEXT_MAX_FONT_SIZE,
            self.RULES_TEXT_MIN_FONT_SIZE,
        )

        for room in self.rooms:
            if not room.body:
                continue
            x, y, width, height = room.body_pixel_box
            self.RULES_TEXT_X = x
            self.RULES_TEXT_Y = y
            self.RULES_TEXT_WIDTH = max(width, 1)
            self.RULES_TEXT_HEIGHT = max(height, 1)
            self.RULES_TEXT_MAX_FONT_SIZE = max(room.body_font_size, 1)
            self.RULES_TEXT_MIN_FONT_SIZE = max(room.body_font_size, 1)
            self.set_metadata(CARD_RULES_TEXT, self._get_room_body_text(room, centered=False if room.inline else None))
            try:
                super()._create_rules_text_layer()
            except ValueError:
                log(f"Could not fit the text of '{room.label}' into its room.")

        (
            self.RULES_TEXT_X,
            self.RULES_TEXT_Y,
            self.RULES_TEXT_WIDTH,
            self.RULES_TEXT_HEIGHT,
            self.RULES_TEXT_MAX_FONT_SIZE,
            self.RULES_TEXT_MIN_FONT_SIZE,
        ) = saved
        self.set_metadata(CARD_RULES_TEXT, full_text)
