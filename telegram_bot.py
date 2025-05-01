import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram Bot Token
BOT_TOKEN = "YOUR_TOKEN"

# Flask API URL
API_URL = "http://127.0.0.1:5000/predict"  # Make sure Flask server is running here

# Function to get full crop recommendation
async def get_full_recommendation(n, p, k, temperature, humidity, moisture, soil_type):
    data = {
        "N": n,
        "P": p,
        "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "moisture": moisture,
        "soil_type": soil_type
    }

    try:
        response = requests.post(API_URL, json=data)
        response.raise_for_status()
        result = response.json()
        print("🔍 API Response:", result)
        return (
            result.get("recommended_crop", "Unknown"),
            result.get("recommended_fertilizer", "Unknown"),
            result.get("next_crop_for_soil_health", "Unknown"),
            result.get("recommended_fertilizer_for_next_crop", "Unknown")
        )
    except Exception as e:
        print("❌ API Error:", e)
        return ("Error", "Error", "Error", "Error")

# /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🌾 Welcome to CropBot!\n\n"
        "Please send your soil data in this format:\n\n"
        "`N,P,K,Temperature,Humidity,Moisture,Soil_Type`\n\n"
        "Example: `40,20,30,25,60,50,Loamy`",
        parse_mode='Markdown'
    )

# Message handler
async def handle_message(update: Update, context: CallbackContext):
    try:
        parts = update.message.text.split(",")
        if len(parts) != 7:
            await update.message.reply_text("❌ Invalid input! Format:\n`N,P,K,Temperature,Humidity,Moisture,Soil_Type`", parse_mode='Markdown')
            return

        # Extract and validate
        n, p, k = map(float, parts[:3])
        temperature = float(parts[3])
        humidity = float(parts[4])
        moisture = float(parts[5])
        soil_type = parts[6].strip()

        crop, fert, next_crop, next_fert = await get_full_recommendation(n, p, k, temperature, humidity, moisture, soil_type)

        # Reply to user
        reply_text = (
            f"✅ *Recommended Crop:* {crop}\n"
            f"🧪 *Recommended Fertilizer:* {fert}\n"
            f"🔄 *Next Crop for Soil Health:* {next_crop}\n"
            f"🌿 *Fertilizer for Next Crop:* {next_fert}"
        )
        await update.message.reply_text(reply_text, parse_mode='Markdown')

    except Exception as e:
        print("❌ Parsing error:", e)
        await update.message.reply_text("⚠️ Error! Make sure your input format is correct.")

# Set up the bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Run bot
print("✅ Telegram Bot is running...")
app.run_polling()
