
def validate_inputs(inputs: dict) -> list[str]:
    required = {
        "country": "Please enter your country.",
        "city": "Please enter your city or region.",
        "business_idea": "Please describe the business you want to start.",
    }
    errors = [message for key, message in required.items() if not inputs.get(key)]

    if len(inputs.get("business_idea", "")) < 8 and inputs.get("business_idea"):
        errors.append("Please describe your business idea in a little more detail.")

    return errors
