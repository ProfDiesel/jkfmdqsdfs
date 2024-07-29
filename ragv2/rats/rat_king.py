

class RatKing:
    pass

class RatPack:
    pass


class Event:
    pass

class ChatEvent(Event):
    pass

class Joined(ChatEvent):
    pass

class Left(ChatEvent):
    pass

class NewMessage(ChatEvent):
    pass

class UserEvent(Event):
    pass

class UserDirectMessage(UserEvent):
    pass

class UserVote(UserEvent):
    pass


async def handle_event(event: Event):
    tracker_id = generate_tracker_id(event)
    dispatch(event)

async def handle_chat_event(event: ChatEvent):
    | clone_on_new_thread
    | process_message
    | gather(rat.process() for rat in rats)
    | self_assess # generate / collect KPIs
    | publish
    | archive_for_non_reg

async def handle_user_direct_message(event: UserDirectMessage):
    pass

async def handle_user_vote(event: UserVote):
    pass