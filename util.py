import random
import string


# Function to generate ids for new user stories:
def generate_id(
        number_of_small_letters=4,
        number_of_capital_letters=2,
        number_of_digits=2,
        number_of_special_chars=2,
        allowed_special_chars=r"_+-!"
        ):
    characters = []
    add_characters(string.ascii_lowercase, number_of_small_letters, characters)
    add_characters(string.ascii_uppercase,
                   number_of_capital_letters, characters)
    add_characters("0123456789", number_of_digits, characters)
    add_characters(allowed_special_chars, number_of_special_chars, characters)
    random.shuffle(characters)
    return ''.join(characters)


# Supporting function of generate_id(...), add characters to output
# as requested by it's caller.
def add_characters(pool, aspect, characters):
    for addition in range(aspect):
        characters.append(random.choice(pool))
