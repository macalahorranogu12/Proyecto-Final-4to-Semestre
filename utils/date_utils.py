from datetime import date


def calculate_age(birthdate_str: str) -> int:

    try:
        birthdate = date.fromisoformat(
            birthdate_str
        )

        today = date.today()

        age = (
            today.year
            - birthdate.year
        )

        if (
            today.month,
            today.day
        ) < (
            birthdate.month,
            birthdate.day
        ):
            age -= 1

        return age

    except Exception:
        return 0