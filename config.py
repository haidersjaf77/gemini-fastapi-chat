import os

# === Environment Config ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")  # or "prod", "staging"
DB_NAME = "users.db" if ENVIRONMENT == "dev" else "prod_users.db"

# === Domain Restrictions ===
SUPPORTED_DOMAINS = ["gmail.com", "outlook.com", "yahoo.com"]  # Add more if needed

# === OTP Settings ===
OTP_VALIDITY_MINUTES = 10
OTP_MAX_RETRIES = 3

# === API Key Config ===
MASKED_API_KEY_LEN = 5
API_KEY_LENGTH = 32
API_KEY_VALIDITY_DAYS = 90

# config.py
num_request = 10  # How many requests allowed per time window
time_period = 60  # In seconds (e.g., 60 = 1 minute)

# === Rate Limiting ===
RATE_LIMITS = {
    "window_seconds": 60,
    "max_requests": 2
}

# === Logging Config ===
LOGGING_LEVEL = "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR

# === Email Templates ===
OTP_EMAIL_HTML = """<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OTP Email</title>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; padding: 20px; }}
        .container {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
        .otp {{ font-weight: bold; font-size: 22px; color: #0073e6; }}
        .footer {{ font-size: 12px; color: #777; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Your OTP Code</h2>
        <p>Your One-Time Password (OTP) is: <span class="otp">{generated_otp}</span></p>
        <p>This OTP is valid for {OTP_VALIDITY_MINUTES} minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
    </div>
</body>
</html>
""".replace("{OTP_VALIDITY_MINUTES}", str(OTP_VALIDITY_MINUTES))
