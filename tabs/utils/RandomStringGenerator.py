import secrets


class RandomStringGenerator:
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    @staticmethod
    def generate_content_playback_nonce() -> str:
        return RandomStringGenerator._generate(RandomStringGenerator.ALPHABET, 16)

    @staticmethod
    def generate_t_parameter() -> str:
        return RandomStringGenerator._generate(RandomStringGenerator.ALPHABET, 12)

    @staticmethod
    def _generate(alphabet: str, length: int) -> str:
        return ''.join(secrets.choice(alphabet) for _ in range(length))

