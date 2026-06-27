from constants import JUMP_DURATION


class Player:
    def __init__(self) -> None:
        self.position: int = 0
        self._jump_steps: int = 0
        self.is_crouching: bool = False

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    @property
    def is_jumping(self) -> bool:
        return self._jump_steps > 0

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def jump(self) -> bool:
        """Initiate a jump. Returns True if the jump was accepted.
        Blocked while crouching or already airborne."""
        if self.is_jumping or self.is_crouching:
            return False
        self._jump_steps = JUMP_DURATION
        return True

    def start_crouch(self) -> bool:
        """Start crouching. Returns True on state change.
        Blocked while airborne."""
        if self.is_crouching or self.is_jumping:
            return False
        self.is_crouching = True
        return True

    def stand_up(self) -> bool:
        """Stand up from a crouch. Returns True on state change."""
        if not self.is_crouching:
            return False
        self.is_crouching = False
        return True

    def step(self) -> None:
        """Advance one position and tick the jump counter."""
        self.position += 1
        if self._jump_steps > 0:
            self._jump_steps -= 1
