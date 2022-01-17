from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.resolver import Resolver

class State():

    def __init__(self, resolver: Resolver):
        self.resolver = resolver
        self.prev_state = None

    def update(self, delta_time, actions):
        pass

    def render(self, surface):
        pass

    def enter_state(self):
        if len(self.resolver.state_stack) > 1:
            self.prev_state = self.resolver.state_stack[-1]
        self.resolver.state_stack.append(self)

    def exit_state(self):
        self.resolver.state_stack.pop()