#!/usr/bin/env python3
"""
Environment Variable Validation Script
Checks if all required environment variables are properly configured
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment file
env_file = Path(".env.poc")
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print("⚠️ No .env.poc file found")

# Required environment variables
REQUIRED_VARS = {
    "MISTRAL_API_KEY": "Mistral AI API key for AI processing",
    "TELEGRAM_BOT_TOKEN": "Telegram bot token for Telegram integration",
    "WHATSAPP_ACCESS_TOKEN": "WhatsApp Business API access token",
    "WHATSAPP_PHONE_NUMBER_ID": "WhatsApp phone number ID"
}

# Optional but recommended variables
OPTIONAL_VARS = {
    "ENVIRONMENT": "Application environment (development/production)",
    "DEBUG": "Debug mode flag",
    "LOG_LEVEL": "Logging level",
    "DATABASE_URL": "Database connection string",
    "REDIS_URL": "Redis connection string"
}

def validate_environment():
    """Validate environment variables"""
    print("\n🔍 Environment Variable Validation")
    print("=" * 50)
    
    # Check required variables
    missing_required = []
    configured_required = []
    
    for var, description in REQUIRED_VARS.items():
        value = os.getenv(var)
        if not value or value.startswith("your_") or value.endswith("_here"):
            missing_required.append(var)
            print(f"❌ {var}: Not configured - {description}")
        else:
            configured_required.append(var)
            # Mask sensitive values
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked_value} - {description}")
    
    # Check optional variables
    print("\n📋 Optional Variables:")
    for var, description in OPTIONAL_VARS.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value} - {description}")
        else:
            print(f"⚪ {var}: Not set - {description}")
    
    # Summary
    print("\n📊 Summary:")
    print(f"✅ Configured required variables: {len(configured_required)}/{len(REQUIRED_VARS)}")
    if missing_required:
        print(f"❌ Missing required variables: {missing_required}")
        print("\n🔧 To configure missing variables:")
        print("1. Edit the .env.poc file")
        print("2. Replace placeholder values with your actual API keys")
        print("3. Restart the Docker containers")
        return False
    else:
        print("🎉 All required environment variables are configured!")
        return True

if __name__ == "__main__":
    validate_environment()