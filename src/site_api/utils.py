import random
import string


def generate_invite_code():
    """Generate a team invite code."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))
