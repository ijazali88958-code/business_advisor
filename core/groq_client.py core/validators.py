

"""Input validation for the Business Launch Advisor application."""

from typing import Any


REQUIRED_FIELDS = (
    "country",
    "city",
    "business_idea",
    "business_size",
    "budget",
    "online_or_physical",
    "experience",
)

ALLOWED_BUSINESS_SIZES = {
    "Micro / home-based",
    "Small",
    "Medium",
    "Large / growing",
}

ALLOWED_ENVIRONMENTS = {
    "Online",
    "Physical location",
    "Both",
}

ALLOWED_EXPERIENCE_LEVELS = {
    "Beginner",
    "Some experience",
    "Experienced",
}


def validate_inputs(inputs: dict[str, Any]) -> list[str]:
    """
    Validate user inputs before generating a business launch plan.

    Returns:
        A list of validation error messages.
        An empty list means the supplied inputs passed these checks.
    """
    errors: list[str] = []

    if not isinstance(inputs, dict):
        return ["Invalid input data. Please submit the form again."]

    # Check that every expected field exists and contains text.
    for field in REQUIRED_FIELDS:
        value = inputs.get(field)

        if not isinstance(value, str):
            errors.append(
                f"Please provide a valid value for "
                f"'{field.replace('_', ' ')}'."
            )
        elif not value.strip():
            errors.append(
                f"Please enter {field.replace('_', ' ')}."
            )

    # Stop additional checks if required fields are missing or invalid.
    if errors:
        return errors

    # Check the selected options against the choices in app.py.
    if inputs["business_size"] not in ALLOWED_BUSINESS_SIZES:
        errors.append("Please select a valid business size.")

    if inputs["online_or_physical"] not in ALLOWED_ENVIRONMENTS:
        errors.append("Please select a valid business environment.")

    if inputs["experience"] not in ALLOWED_EXPERIENCE_LEVELS:
        errors.append("Please select a valid experience level.")

    # Set reasonable limits for text inputs.
    text_limits = {
        "country": 100,
        "city": 150,
        "business_idea": 2000,
        "budget": 100,
    }

    for field, max_length in text_limits.items():
        value = inputs[field].strip()

        if len(value) > max_length:
            errors.append(
                f"{field.replace('_', ' ').capitalize()} must be "
                f"{max_length} characters or fewer."
            )

    return errors
