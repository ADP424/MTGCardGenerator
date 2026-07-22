from contextlib import ExitStack, contextmanager

from PIL import Image

from constants import CARD_FRAME_LAYOUT_EXTRAS
from log import log
from model.dungeon.Dungeon import Dungeon
from model.dungeon.ExpandedDungeon import OPPOSITE_DIRECTION, ExpandedDungeon
from model.Layer import Layer
from model.regular.RegularCard import RegularCard


class ExpandedDungeonLocal(ExpandedDungeon):
    """
    A dungeon that spans an arbitrary grid of cards: each card is still one `Rules Text`
    cell/spreadsheet row, laid out on its own grid, but it can connect to other cards' rooms via
    doorways. The downside is that row sizing isn't assured across cards.
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
        self._own_card_key = self._card_key_of(metadata)

        self._qualified_targets: dict[str, tuple[str, str, str | None]] = {}

        self.sibling_cards: dict[str, "ExpandedDungeonLocal"] = {}
        self.resolved_door_targets: dict[str, tuple[str | None, "ExpandedDungeonLocal", "Dungeon.Room"]] = {}

        self._doors_built: set[frozenset] = set()

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

    def _floor_bounds(self) -> tuple[int, int, int, int]:
        """
        This card's own usable floor bounds: the floor rectangle of its one card face.
        """

        return self._face_floor_bounds(self.row_band, self.column_position)

    def _is_bottom_row(self) -> bool:
        return self.row_band == "bottom"

    def _qualified_door_target(self, card_key: str, room_id: str, direction: str | None) -> str:
        """
        Keep a qualified target's card key in the identifier, and remember the pieces so
        `link_siblings` can resolve it to the real sibling card/room later.
        """

        identifier = f"{card_key.lower()}:{room_id}"
        self._qualified_targets[identifier] = (card_key, room_id, direction)
        return identifier

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
        Same as `Dungeon._door_targets_for`, except a qualified `{to=...}` identifier is excluded first.
        """

        with self._without_qualified_targets(room):
            return super()._door_targets_for(room, min_overlap, log_problems)

    def _vertical_door_targets_for(self, room: "Dungeon.Room", log_problems: bool = False):
        """
        Same as `Dungeon._vertical_door_targets_for`, except a qualified `{to=...}` identifier
        is excluded first.
        """

        with self._without_qualified_targets(room):
            return super()._vertical_door_targets_for(room, log_problems)

    def _horizontal_door_pairs(self):
        """
        Same as `Dungeon._horizontal_door_pairs`, except every room's qualified `{to=...}`
        identifiers are excluded first.
        """

        with ExitStack() as stack:
            for room in self.rooms:
                stack.enter_context(self._without_qualified_targets(room))
            return super()._horizontal_door_pairs()

    def _room_names(self, source: "Dungeon.Room", target: "Dungeon.Room", target_card: "Dungeon" = None) -> bool:
        """
        Same as `Dungeon._room_names`, except `target`'s identifiers are qualified with
        `target_card`'s card key when it's given.
        """

        if source.door_targets is None:
            return False
        if target_card is None or target_card is self:
            return super()._room_names(source, target, target_card)
        target_identifiers = {f"{target_card._own_card_key.lower()}:{room_id}" for room_id in target.ids}
        return any(identifier in target_identifiers for identifier in source.door_targets)

    def link_siblings(self, sibling_cards: dict[str, "RegularCard"]):
        """
        Resolve this card's qualified `{to=...}` targets to the actual sibling `ExpandedDungeonLocal`
        object(s) they name, store the results in `self.sibling_cards`, then build the cross-card
        doorways.

        Parameters
        ----------
        sibling_cards : dict[str, RegularCard]
            Every card in this card's set, keyed by `get_card_key()`-style card key.
        """

        by_lower_key = self._siblings_by_lower_key(sibling_cards)

        def resolve_card(card_key: str) -> "ExpandedDungeonLocal | None":
            if card_key in self.sibling_cards:
                return self.sibling_cards[card_key]
            card = by_lower_key.get(card_key.lower())
            if card is None:
                log(f"'{self._own_card_key}' has a doorway to '{card_key}', which isn't a card in this set.")
                return None
            if not isinstance(card, ExpandedDungeonLocal):
                log(f"'{self._own_card_key}' has a doorway to '{card_key}', which isn't an expanded dungeon card.")
                return None
            self.sibling_cards[card_key] = card
            return card

        def resolve_room(card_key: str, room_id: str) -> tuple["ExpandedDungeonLocal", "Dungeon.Room"] | None:
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

        def touches(room: "Dungeon.Room", card: "ExpandedDungeonLocal", edge: str) -> bool:
            if edge == "up":
                return room.tile_y0 == 0
            if edge == "down":
                return room.tile_y1 == card.GRID_ROWS
            if edge == "left":
                return room.tile_x0 == 0
            return room.tile_x1 == card.GRID_COLUMNS

        def edge_for(
            room: "Dungeon.Room",
            other_card: "ExpandedDungeonLocal",
            other: "Dungeon.Room",
            explicit_direction: str | None,
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

            candidates = [
                direction
                for direction in ("up", "down", "left", "right")
                if touches(room, self, direction) and touches(other, other_card, OPPOSITE_DIRECTION[direction])
            ]
            return candidates[0] if len(candidates) == 1 else None

        def build(
            room: "Dungeon.Room",
            explicit_direction: str | None,
            other_card: "ExpandedDungeonLocal",
            other: "Dungeon.Room",
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
            horizontal = direction in ("up", "down")
            mutual = self._is_mutual_door(room, other, other_card)

            if horizontal:
                shared_0, shared_1 = self._get_shared_wall_columns(room, other)
                opening, minimum = self.DOOR_OPENING_COLUMNS, self.DOOR_MIN_SHARED_COLUMNS
                fix = "Widen"
            else:
                shared_0, shared_1 = self._get_shared_wall_rows(room, other)
                opening, minimum = self.DOOR_OPENING_ROWS, self.DOOR_MIN_SHARED_ROWS
                fix = "Heighten"
            shared = shared_1 - shared_0
            if shared < minimum:
                log(
                    f"'{self._own_card_key}: {room.label}' and '{other_card._own_card_key}: {other.label}' "
                    f"only share {shared} tile(s) of wall, but a doorway needs {minimum}. {fix} one of the "
                    "rooms, or leave them without a doorway."
                )
                return

            tile_start = shared_0 + (shared - opening) // 2
            forward = direction in ("down", "right")
            mutual_arrow = "up_down" if horizontal else "left_right"
            this_arrow = mutual_arrow if mutual else direction
            other_arrow = mutual_arrow if mutual else OPPOSITE_DIRECTION[direction]
            halves = ("top", "bottom") if horizontal else ("left", "right")
            this_half, other_half = halves if forward else halves[::-1]

            if horizontal:
                this_seam = self.GRID_ROWS if forward else 0
                other_seam = 0 if forward else other_card.GRID_ROWS
                this_door = Dungeon.Door(
                    tile_start,
                    tile_start + opening,
                    this_seam,
                    arrows_on and room.arrows,
                    axis="horizontal",
                    arrow_direction=this_arrow,
                    split_half=this_half,
                )
                other_door = Dungeon.Door(
                    tile_start,
                    tile_start + opening,
                    other_seam,
                    arrows_on and other.arrows,
                    axis="horizontal",
                    arrow_direction=other_arrow,
                    split_half=other_half,
                )
                this_gaps = room.bottom_pixel_gaps if forward else room.top_pixel_gaps
                other_gaps = other.top_pixel_gaps if forward else other.bottom_pixel_gaps
                this_gaps.append((self._door_start_x(this_door), self._door_end_x(this_door)))
                other_gaps.append((other_card._door_start_x(other_door), other_card._door_end_x(other_door)))
            else:
                this_seam = self.GRID_COLUMNS if forward else 0
                other_seam = 0 if forward else other_card.GRID_COLUMNS
                this_door = Dungeon.Door(
                    this_seam,
                    0,
                    tile_start,
                    arrows_on and room.arrows,
                    axis="vertical",
                    tile_y1=tile_start + opening,
                    arrow_direction=this_arrow,
                    split_half=this_half,
                )
                other_door = Dungeon.Door(
                    other_seam,
                    0,
                    tile_start,
                    arrows_on and other.arrows,
                    axis="vertical",
                    tile_y1=tile_start + opening,
                    arrow_direction=other_arrow,
                    split_half=other_half,
                )
                this_gaps = room.right_pixel_gaps if forward else room.left_pixel_gaps
                other_gaps = other.left_pixel_gaps if forward else other.right_pixel_gaps
                this_gaps.append((self._door_start_y(this_door), self._door_end_y(this_door)))
                other_gaps.append((other_card._door_start_y(other_door), other_card._door_end_y(other_door)))

            self.doors.append(this_door)
            other_card.doors.append(other_door)

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

        seam_y = self._get_seam_y(door)
        half = self.DOORWAY_PIECE_HEIGHT // 2
        clip = (seam_y - half, seam_y) if door.split_half == "top" else (seam_y, seam_y + half)
        stamp_wall_piece(
            shape,
            effect,
            self.WALL_HORIZONTAL_DOORWAY_PIECE,
            (self._door_center_x(door) - self.DOORWAY_PIECE_WIDTH // 2, seam_y - half),
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

        seam_x = self._get_seam_x(door)
        half = self.DOORWAY_PIECE_HEIGHT // 2
        clip = (seam_x - half, seam_x) if door.split_half == "left" else (seam_x, seam_x + half)
        stamp_wall_piece(
            shape,
            effect,
            self.WALL_VERTICAL_DOORWAY_PIECE,
            (seam_x - half, self._door_center_y(door) - self.DOORWAY_PIECE_WIDTH // 2),
            (self.DOORWAY_PIECE_HEIGHT, self.DOORWAY_PIECE_WIDTH),
            clip,
            clip_axis_vertical=False,
        )

    def _stamp_outer_wall(self, shape: Image.Image, effect: Image.Image, stamp_wall_piece):
        """
        Stamp this card's outer wall border, using its own parsed position.
        """

        self._stamp_outer_wall_face(shape, effect, stamp_wall_piece, self.row_band, self.column_position)
