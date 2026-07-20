from contextlib import contextmanager

from PIL import Image

from constants import (
    CARD_ADDITIONAL_TITLES,
    CARD_DESCRIPTOR,
    CARD_FRAME_LAYOUT_EXTRAS,
    CARD_TITLE,
)
from log import log
from model.dungeon.Dungeon import Dungeon
from model.Layer import Layer
from model.regular.RegularCard import RegularCard
from utils import get_card_key

OPPOSITE_DIRECTION = {"up": "down", "down": "up", "left": "right", "right": "left"}
EDGE_NAMES = frozenset(OPPOSITE_DIRECTION)


class ExpandedDungeon(Dungeon):
    """
    A dungeon that spans an arbitrary grid of cards: each card is still one `Rules Text`
    cell/spreadsheet row, laid out on its own grid, but it can connect to other cards' rooms via
    doorways.

    Attributes
    ----------
    metadata : dict[str, str | list], optional
        Information about the card (title, mana cost, rules text, frame, etc.)

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

    def __init__(
        self,
        metadata: dict[str, str | list["RegularCard"]] = None,
        art_layer: Layer = None,
        frame_layers: list[Layer] = None,
        collector_layers: list[Layer] = None,
        text_layers: list[Layer] = None,
        overlay_layers: list[Layer] = None,
    ):
        self._own_card_key = get_card_key(
            (metadata or {}).get(CARD_TITLE, ""),
            (metadata or {}).get(CARD_ADDITIONAL_TITLES, ""),
            (metadata or {}).get(CARD_DESCRIPTOR, ""),
        )

        # Every qualified {to=...} target this card's rooms use
        self._qualified_targets: dict[str, tuple[str, str, str | None]] = {}

        # Sibling cards/rooms this card's rooms connect to
        self.sibling_cards: dict[str, "ExpandedDungeon"] = {}
        self.resolved_door_targets: dict[str, tuple[str | None, "ExpandedDungeon", "Dungeon.Room"]] = {}

        # Cross-card room pairs
        self._doors_built: set[frozenset] = set()

        # This card's position in the overall arrangement of all connected cards
        self.row_band, self.has_title, self.column_position = self._parse_position(metadata)

        super().__init__(metadata, art_layer, frame_layers, collector_layers, text_layers, overlay_layers)

    def _parse_position(self, metadata: dict[str, str | list["RegularCard"]] | None) -> tuple[str, bool, str]:
        """
        Parse this card's `(row_band, has_title, column_position)` from the `"top title left"` /
        `"bottom middle"` / etc. token `main.py` strips out of the `Frame Layout` column into
        `CARD_FRAME_LAYOUT_EXTRAS`.
        """

        for extra in (metadata or {}).get(CARD_FRAME_LAYOUT_EXTRAS, []):
            words = extra.split()
            if not words or words[0] not in ("top", "middle", "bottom"):
                continue
            row_band = words[0]
            has_title = len(words) > 1 and words[1] == "title"
            column_position = words[-1]
            return row_band, has_title, column_position

        log(
            f"'{self._own_card_key}' has an Expanded Dungeon Frame Layout with no recognized "
            "position (e.g. 'Expanded Dungeon Top Title Left', 'Expanded Dungeon Bottom Middle'). "
            "Skipping..."
        )
        return "middle", False, "closed"

    def _init_grid_constants(self):
        """
        Override `Dungeon`'s tile grid with this specific card's own usable floor bounds.
        """

        self.TILE_SIZE = 75

        left_x = 150 if self.column_position in ("closed", "left") else 0
        right_x = 1350 if self.column_position in ("closed", "right") else 1500
        top_y = 300 if self.row_band == "top" else 0
        bottom_y = 1800 if self.row_band == "bottom" else 2100

        self.GRID_ORIGIN_X = left_x
        self.GRID_ORIGIN_Y = top_y
        self.GRID_COLUMNS = (right_x - left_x) // self.TILE_SIZE
        self.GRID_ROWS = (bottom_y - top_y) // self.TILE_SIZE

    def _init_wall_constants(self):
        """
        Same as `Dungeon._init_wall_constants`, except every asset path points at
        `images/frames/dungeon/expanded/wall`.
        """

        # Walls
        self.WALL_PATH = "dungeon/expanded/wall"
        self.WALL_SHAPE_FOLDER = "shape"
        self.WALL_EFFECT_FOLDER = "effect"
        self.WALL_TEXTURE_PREFIX = "dungeon/expanded/wall/texture/"
        self.WALL_OUTER_PIECE = "outer"

        # Doorways
        self.WALL_HORIZONTAL_DOORWAY_PIECE = "horizontal_doorway"
        self.WALL_VERTICAL_DOORWAY_PIECE = "vertical_doorway"
        self.DOOR_OPENING_COLUMNS = 2
        self.DOOR_OPENING_ROWS = 2
        self.DOORWAY_PIECE_WIDTH = 225
        self.DOORWAY_PIECE_HEIGHT = 150
        self.DOOR_MIN_SHARED_COLUMNS = self.DOOR_OPENING_COLUMNS + 2
        self.DOOR_MIN_SHARED_ROWS = self.DOOR_OPENING_ROWS + 2

        # Arrows
        self.ARROW_PATHS = {
            "up": "dungeon/expanded/wall/arrow/up",
            "down": "dungeon/expanded/wall/arrow/down",
            "left": "dungeon/expanded/wall/arrow/left",
            "right": "dungeon/expanded/wall/arrow/right",
            "left_right": "dungeon/expanded/wall/arrow/left_right",
            "up_down": "dungeon/expanded/wall/arrow/up_down",
        }
        self.ARROW_WIDTH = 75
        self.ARROW_HEIGHT = 75
        self.ARROW_OFFSET_Y = 0
        self.ARROW_OFFSET_X = 0

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

        super().create_layers(
            create_art_layer,
            create_frame_layers,
            create_watermark_layer,
            create_rarity_symbol_layer,
            create_footer_layer and self.row_band == "bottom",
            create_mana_cost_layer,
            create_title_layer and self.has_title,
            create_type_layer,
            create_rules_text_layer,
            create_power_toughness_layer,
            create_overlay_layers,
            create_wall_layers,
            create_arrow_layers,
            create_room_name_layers,
        )

    def _parse_door_targets(self, value: str) -> list[str]:
        """
        Parse a `{to=...}` value the same way `Dungeon` does, except each comma-separated target
        may also have another card's key: `Card Key: Room Id`, optionally followed by
        `: direction` (one of `up`/`down`/`left`/`right`).
        """

        if value.lower().strip() in ("", "none", "-"):
            return []

        identifiers: list[str] = []
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue

            card_key, room_id, direction = self._split_qualified_target(part)
            if card_key is None:
                identifiers.append(room_id)
                continue

            identifier = f"{card_key.lower()}:{room_id}"
            identifiers.append(identifier)
            self._qualified_targets[identifier] = (card_key, room_id, direction)

        return identifiers

    def _split_qualified_target(self, value: str) -> tuple[str | None, str, str | None]:
        """
        Split a `{to=...}` target into `(card_key, room_id, direction)`: `card_key` is `None` if
        the target is unqualified (or qualified with this card's own key, which names a room on
        this card just like an unqualified target would)

        The `direction` is the explicit edge a doorway sits on, given as a third colon-separated segment.

        Parameters
        ----------
        value : str
            One comma-separated target, already stripped of surrounding whitespace.
        """

        if ":" not in value:
            return None, value.lower(), None

        parts = [part.strip() for part in value.split(":")]
        direction = None
        if len(parts) > 1 and parts[-1].lower() in EDGE_NAMES:
            direction = parts.pop().lower()

        card_key, room_id = ":".join(parts[:-1]), parts[-1]
        card_key, room_id = card_key.strip(), room_id.strip().lower()
        if not card_key or card_key.lower() == self._own_card_key.lower():
            return None, room_id, direction
        return card_key, room_id, direction

    def _without_qualified_targets(self, room: "Dungeon.Room"):
        """
        Temporarily strip `{to=...}` identifiers out of `room.door_targets`,
        then restore it at the end.
        """

        @contextmanager
        def manager():
            original = room.door_targets
            if original is not None:
                room.door_targets = [identifier for identifier in original if identifier not in self._qualified_targets]
            try:
                yield
            finally:
                room.door_targets = original

        return manager()

    def _door_targets_for(self, room: "Dungeon.Room", min_overlap=None, log_problems: bool = False):
        """
        Same as `Dungeon._door_targets_for`, except a qualified `{to=...}` identifier is excluded
        first -- see `_without_qualified_targets`.
        """

        with self._without_qualified_targets(room):
            return super()._door_targets_for(room, min_overlap, log_problems)

    def _vertical_door_targets_for(self, room: "Dungeon.Room", log_problems: bool = False):
        """
        Same as `Dungeon._vertical_door_targets_for`, except a qualified `{to=...}` identifier is
        excluded first -- see `_without_qualified_targets`.
        """

        with self._without_qualified_targets(room):
            return super()._vertical_door_targets_for(room, log_problems)

    def _room_names(self, source: "Dungeon.Room", target: "Dungeon.Room", target_card: "Dungeon" = None) -> bool:
        """
        Same as `Dungeon._room_names`, except `target`'s identifiers are qualified with
        `target_card`'s card key when it's given (a cross-card check, as used by
        `_build_cross_card_doors`'s mutual-doorway check) rather than looked up in this card's own
        `room_ids`.
        """

        if source.door_targets is None:
            return False
        if target_card is None or target_card is self:
            return super()._room_names(source, target, target_card)
        target_identifiers = {f"{target_card._own_card_key.lower()}:{room_id}" for room_id in target.ids}
        return any(identifier in target_identifiers for identifier in source.door_targets)

    def link_siblings(self, sibling_cards: dict[str, "RegularCard"]):
        """
        Resolve this card's qualified `{to=...}` targets to the actual sibling `ExpandedDungeon`
        object(s) they name, then store the results in `self.sibling_cards`.

        Parameters
        ----------
        sibling_cards : dict[str, RegularCard]
            Every card in this card's set, keyed by `get_card_key()`-style card key -- the same
            dict `main.py` already builds per set (`card_sets[card_set]`).
        """

        by_lower_key = {key.lower(): card for key, card in sibling_cards.items()}

        def resolve_card(card_key: str) -> "ExpandedDungeon | None":
            if card_key in self.sibling_cards:
                return self.sibling_cards[card_key]
            card = by_lower_key.get(card_key.lower())
            if card is None:
                log(f"'{self._own_card_key}' has a doorway to '{card_key}', which isn't a card in this set.")
                return None
            if not isinstance(card, ExpandedDungeon):
                log(f"'{self._own_card_key}' has a doorway to '{card_key}', which isn't an expanded dungeon card.")
                return None
            self.sibling_cards[card_key] = card
            return card

        def resolve_room(card_key: str, room_id: str) -> tuple["ExpandedDungeon", "Dungeon.Room"] | None:
            card = resolve_card(card_key)
            if card is None:
                return None
            room = card.room_ids.get(room_id)
            if room is None:
                log(f"'{self._own_card_key}' has a doorway to '{card_key}: {room_id}', which isn't a room there.")
                return None
            return card, room

        for identifier, (card_key, room_id, direction) in self._qualified_targets.items():
            resolved = resolve_room(card_key, room_id)
            if resolved is not None:
                other_card, other_room = resolved
                self.resolved_door_targets[identifier] = (direction, other_card, other_room)

        self._build_cross_card_doors()

    def _build_cross_card_doors(self):
        """
        Build a `Dungeon.Door` on this card's edge, and the matching `Dungeon.Door` on the target
        card's opposite edge, for every resolved cross-card `{to=...}` target.
        """

        arrows_on = "arrowless" not in self.get_metadata(CARD_FRAME_LAYOUT_EXTRAS, [])

        def touches(room: "Dungeon.Room", card: "ExpandedDungeon", edge: str) -> bool:
            if edge == "up":
                return room.tile_y0 == 0
            if edge == "down":
                return room.tile_y1 == card.GRID_ROWS
            if edge == "left":
                return room.tile_x0 == 0
            return room.tile_x1 == card.GRID_COLUMNS

        def edge_for(
            room: "Dungeon.Room", other_card: "ExpandedDungeon", other: "Dungeon.Room", explicit_direction: str | None
        ) -> str | None:
            if explicit_direction is not None:
                opposite = OPPOSITE_DIRECTION[explicit_direction]
                if not touches(room, self, explicit_direction) or not touches(other, other_card, opposite):
                    log(
                        f"'{self._own_card_key}: {room.label}' has a doorway to '{other_card._own_card_key}: "
                        f"{other.label}' explicitly on its '{explicit_direction}' edge, but at least one of "
                        "the two rooms doesn't actually touch that edge on its own card."
                    )
                    return None
                return explicit_direction

            candidates = []
            if room.tile_y0 == 0 and other.tile_y1 == other_card.GRID_ROWS:
                candidates.append("up")
            if room.tile_y1 == self.GRID_ROWS and other.tile_y0 == 0:
                candidates.append("down")
            if room.tile_x0 == 0 and other.tile_x1 == other_card.GRID_COLUMNS:
                candidates.append("left")
            if room.tile_x1 == self.GRID_COLUMNS and other.tile_x0 == 0:
                candidates.append("right")
            if len(candidates) == 1:
                return candidates[0]
            return None

        def build(
            room: "Dungeon.Room", explicit_direction: str | None, other_card: "ExpandedDungeon", other: "Dungeon.Room"
        ):
            pair = frozenset((id(room), id(other)))
            if pair in self._doors_built or pair in other_card._doors_built:
                return

            direction = edge_for(room, other_card, other, explicit_direction)
            if direction is None:
                if explicit_direction is None:
                    log(
                        f"'{self._own_card_key}: {room.label}' has a doorway to '{other_card._own_card_key}: "
                        f"{other.label}', but which edge it's on is ambiguous -- give it explicitly, e.g. "
                        f"'{{to={other_card._own_card_key}: {other.label}: right}}'."
                    )
                return

            self._doors_built.add(pair)

            if direction in ("up", "down"):
                shared_c0, shared_c1 = self._get_shared_wall_columns(room, other)
                shared = shared_c1 - shared_c0
                if shared < self.DOOR_MIN_SHARED_COLUMNS:
                    log(
                        f"'{self._own_card_key}: {room.label}' and '{other_card._own_card_key}: {other.label}' "
                        f"only share {shared} tile(s) of wall, but a doorway needs "
                        f"{self.DOOR_MIN_SHARED_COLUMNS}. Widen one of the rooms, or leave them without a doorway."
                    )
                    return

                mutual = self._is_mutual_door(room, other, other_card)
                opening = self.DOOR_OPENING_COLUMNS
                tile_x0 = shared_c0 + (shared - opening) // 2
                this_tile_y = self.GRID_ROWS if direction == "down" else 0
                other_tile_y = 0 if direction == "down" else other_card.GRID_ROWS
                this_half = "top" if direction == "down" else "bottom"
                other_half = "bottom" if direction == "down" else "top"
                this_arrow_direction = "up_down" if mutual else direction
                other_arrow_direction = "up_down" if mutual else OPPOSITE_DIRECTION[direction]
                this_show_arrow = arrows_on and room.arrows
                other_show_arrow = arrows_on and other.arrows

                door = Dungeon.Door(
                    tile_x0,
                    tile_x0 + opening,
                    this_tile_y,
                    this_show_arrow,
                    axis="horizontal",
                    arrow_direction=this_arrow_direction,
                    split_half=this_half,
                )
                self.doors.append(door)
                gap = (self._door_start_x(door), self._door_end_x(door))
                if direction == "down":
                    room.bottom_pixel_gaps.append(gap)
                else:
                    room.top_pixel_gaps.append(gap)

                other_door = Dungeon.Door(
                    tile_x0,
                    tile_x0 + opening,
                    other_tile_y,
                    other_show_arrow,
                    axis="horizontal",
                    arrow_direction=other_arrow_direction,
                    split_half=other_half,
                )
                other_card.doors.append(other_door)
                other_gap = (other_card._door_start_x(other_door), other_card._door_end_x(other_door))
                if direction == "down":
                    other.top_pixel_gaps.append(other_gap)
                else:
                    other.bottom_pixel_gaps.append(other_gap)
            else:
                shared_r0, shared_r1 = self._get_shared_wall_rows(room, other)
                shared = shared_r1 - shared_r0
                if shared < self.DOOR_MIN_SHARED_ROWS:
                    log(
                        f"'{self._own_card_key}: {room.label}' and '{other_card._own_card_key}: {other.label}' "
                        f"only share {shared} tile(s) of wall, but a doorway needs "
                        f"{self.DOOR_MIN_SHARED_ROWS}. Heighten one of the rooms, or leave them without a doorway."
                    )
                    return

                mutual = self._is_mutual_door(room, other, other_card)
                opening = self.DOOR_OPENING_ROWS
                tile_y0 = shared_r0 + (shared - opening) // 2
                this_tile_x = self.GRID_COLUMNS if direction == "right" else 0
                other_tile_x = 0 if direction == "right" else other_card.GRID_COLUMNS
                this_half = "left" if direction == "right" else "right"
                other_half = "right" if direction == "right" else "left"
                this_arrow_direction = "left_right" if mutual else direction
                other_arrow_direction = "left_right" if mutual else OPPOSITE_DIRECTION[direction]
                this_show_arrow = arrows_on and room.arrows
                other_show_arrow = arrows_on and other.arrows

                door = Dungeon.Door(
                    this_tile_x,
                    0,
                    tile_y0,
                    this_show_arrow,
                    axis="vertical",
                    tile_y1=tile_y0 + opening,
                    arrow_direction=this_arrow_direction,
                    split_half=this_half,
                )
                self.doors.append(door)
                gap = (self._door_start_y(door), self._door_end_y(door))
                if direction == "right":
                    room.right_pixel_gaps.append(gap)
                else:
                    room.left_pixel_gaps.append(gap)

                other_door = Dungeon.Door(
                    other_tile_x,
                    0,
                    tile_y0,
                    other_show_arrow,
                    axis="vertical",
                    tile_y1=tile_y0 + opening,
                    arrow_direction=other_arrow_direction,
                    split_half=other_half,
                )
                other_card.doors.append(other_door)
                other_gap = (other_card._door_start_y(other_door), other_card._door_end_y(other_door))
                if direction == "right":
                    other.left_pixel_gaps.append(other_gap)
                else:
                    other.right_pixel_gaps.append(other_gap)

        for room in self.rooms:
            if room.door_targets is None:
                continue
            for identifier in room.door_targets:
                resolved = self.resolved_door_targets.get(identifier)
                if resolved is not None:
                    build(room, *resolved)

    def _stamp_horizontal_doorway(
        self, shape: Image.Image, effect: Image.Image, stamp_wall_piece, door: "Dungeon.Door"
    ):
        """
        Same as `Dungeon._stamp_horizontal_doorway`, except a cross-card doorway only stamps its
        own half of the doorway piece.
        """

        if door.split_half is None:
            super()._stamp_horizontal_doorway(shape, effect, stamp_wall_piece, door)
            return

        position = (
            self._door_center_x(door) - self.DOORWAY_PIECE_WIDTH // 2,
            self._get_seam_y(door) - self.DOORWAY_PIECE_HEIGHT // 2,
        )
        half_height = self.DOORWAY_PIECE_HEIGHT // 2
        seam_y = self._get_seam_y(door)
        clip = (seam_y - half_height, seam_y) if door.split_half == "top" else (seam_y, seam_y + half_height)
        stamp_wall_piece(
            shape,
            effect,
            self.WALL_HORIZONTAL_DOORWAY_PIECE,
            position,
            (self.DOORWAY_PIECE_WIDTH, self.DOORWAY_PIECE_HEIGHT),
            clip,
            clip_axis_vertical=True,
        )

    def _stamp_vertical_doorway(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece, door: "Dungeon.Door"):
        """
        Same as `Dungeon._stamp_vertical_doorway`, except a cross-card doorway only stamps its
        own half of the doorway piece.
        """

        if door.split_half is None:
            super()._stamp_vertical_doorway(shape, effect, stamp_wall_piece, door)
            return

        position = (
            self._get_seam_x(door) - self.DOORWAY_PIECE_HEIGHT // 2,
            self._door_center_y(door) - self.DOORWAY_PIECE_WIDTH // 2,
        )
        half_width = self.DOORWAY_PIECE_HEIGHT // 2
        seam_x = self._get_seam_x(door)
        clip = (seam_x - half_width, seam_x) if door.split_half == "left" else (seam_x, seam_x + half_width)
        stamp_wall_piece(
            shape,
            effect,
            self.WALL_VERTICAL_DOORWAY_PIECE,
            position,
            (self.DOORWAY_PIECE_HEIGHT, self.DOORWAY_PIECE_WIDTH),
            clip,
            clip_axis_vertical=False,
        )

    def _stamp_outer_wall(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece):
        """
        Stamp the card's outer wall border from `wall/{shape,effect}/outer/{row_band}/
        {column_position}`, using this card's own parsed position.
        """

        if self.row_band == "middle" and self.column_position == "middle":
            return

        piece = f"{self.WALL_OUTER_PIECE}/{self.row_band}/{self.column_position}"
        stamp_wall_piece(shape, effect, piece, (0, 0), (self.CARD_WIDTH, self.CARD_HEIGHT))
