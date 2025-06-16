from loguru import logger
logger.info("Initializing state machine...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


import storage


class State:
    def __init__(self, name):
        self.name = name

    def on_enter(self):
        logger.debug(f"Enter state: {self.name}")

    def on_exit(self):
        logger.debug(f"Exit state: {self.name}")


class StateMachine:
    def __init__(self):
        self.states = {}
        self.transitions = {}
        self.user_states = {}  # user_id -> current State object

    def add_state(self, state):
        self.states[state.name] = state

    def add_transition(self, from_state, to_state, trigger):
        self.transitions.setdefault(from_state, {})[trigger] = to_state

    def set_initial_state(self, user_id, state_name):
        state = self.states[state_name]
        self.user_states[user_id] = state
        state.on_enter()

    def trigger(self, user_id, event):
        if user_id not in self.user_states:
            print(f"User {user_id} does not have current state.")
            return

        current_state = self.user_states[user_id]
        current_state_name = current_state.name

        if current_state_name in self.transitions:
            if event in self.transitions[current_state_name]:
                new_state_name = self.transitions[current_state_name][event]
                current_state.on_exit()
                new_state = self.states[new_state_name]
                self.user_states[user_id] = new_state
                new_state.on_enter()
            else:
                print(f"No transition by trigger '{event}' from state '{current_state_name}'")
        else:
            print(f"No transitions from state '{current_state_name}'")

    def get_state(self, user_id):
        state = self.user_states.get(user_id)
        return state.name if state else None


if __name__ == "__main__":
    logger.error("This script is intended to be imported as a module, not run directly.")
    exit(1)


# Создаём состояния
greetings = State("Greetings")
setup_end = State("Setup End")
idle = State("Idle")
view_event_data = State("View event data")
edit_data = State("Edit data")
choose_event = State("Choose event")

sm = StateMachine()

sm.add_state(greetings)
sm.add_transition("Greetings", "Setup End", "continue")

sm.add_state(setup_end)
sm.add_transition("Setup End", "Idle", "continue")

sm.add_state(idle)
sm.add_transition("Idle", "View event data", "Add event")
sm.add_transition("Idle", "Choose event", "Remove event")

sm.add_state(view_event_data)
sm.add_transition("View event data", "Idle", "cancel")
sm.add_transition("View event data", "Edit data", "edit")
sm.add_transition("View event data", "Idle", "confirm")

sm.add_state(edit_data)
sm.add_transition("Edit data", "View event data", "input data")

sm.add_state(choose_event)
sm.add_transition("Choose event", "Idle", "cancel")
sm.add_transition("Choose event", "Idle", "event have chosen")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

storage.set_storage('state_machine', sm)