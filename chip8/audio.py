from pygame import mixer


class Audio:
    """Audio processor for the CHIP-8."""

    def __init__(self, mute: bool = False) -> None:
        self.timer = 0
        self.mute = mute
        mixer.init()
        self.plays = mixer.Sound("assets/beep.wav")

    def update(self) -> None:
        """Decrement the sound timer if it's greater than zero."""
        if self.timer > 0:
            self.timer -= 1
            self.play()

    def play(self) -> None:
        """Play a sound if the sound timer is greater than zero."""
        if not self.mute:
            self.plays.play()
