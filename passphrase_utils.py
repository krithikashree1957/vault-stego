# passphrase_utils.py

import secrets

WORDLIST = [
    "apple", "brave", "cloud", "delta", "eagle", "flame", "grape", "haven",
    "ivory", "joker", "karma", "lemon", "mango", "noble", "ocean", "piano",
    "quilt", "river", "storm", "tiger", "umbra", "vivid", "whale", "xenon",
    "yield", "zebra", "amber", "bloom", "coral", "dune", "ember", "frost",
    "glow", "honey", "iris", "jazz", "kite", "lunar", "maple", "nova",
    "onyx", "pearl", "quest", "raven", "solar", "tempo", "unity", "vapor",
    "willow", "xylo", "yeti", "zen", "arctic", "blaze", "cedar", "drift",
    "echo", "fable", "grove", "horizon", "indigo", "jungle", "knight", "lotus",
    "meadow", "nectar", "opal", "pixel", "quartz", "ridge", "spark", "trail",
    "umber", "velvet", "wander", "xerus", "yonder", "zephyr", "anchor", "breeze",
    "canyon", "dawn", "ember", "falcon", "granite", "harbor", "ink", "jade",
    "kelp", "lagoon", "mist", "north", "olive", "prairie", "quill", "reef",
    "summit", "thicket", "urban", "valley", "wisp", "yolk", "zest", "aurora"
]

def generate_passphrase(num_words: int = 4, separator: str = "-") -> str:
    """
    Generates a random passphrase from the wordlist using a
    cryptographically secure random choice (not the regular random module).
    """
    words = [secrets.choice(WORDLIST) for _ in range(num_words)]
    return separator.join(words)

if __name__ == "__main__":
    for _ in range(5):
        print(generate_passphrase())