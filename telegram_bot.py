import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace with your Telegram Bot Token
BOT_TOKEN = "7710870583:AAE-G3V9Wh8LgGrV-NLgvjzGxYhTY_kpytY"

# Function to get crop recommendation from Flask API
async def get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    url = "http://127.0.0.1:5000/predict"  # Ensure Flask is running
    data = {
        "N": n, "P": p, "K": k,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }
    
    response = requests.post(url, json=data)
    
    # Debugging: Print response details
    print("🔍 API Response Status Code:", response.status_code)
    print("🔍 API Response Text:", response.text)

    try:
        response_json = response.json()
        print("🔍 Parsed JSON:", response_json)
        return response_json.get("recommended_crop", "Sorry, I couldn't determine the crop.")
    except Exception as e:
        print("❌ Error parsing JSON:", e)
        return "❌ Error: Invalid response from API."



# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🌱 Welcome! Send soil details like:\n\n"
                                    "N,P,K,Temperature,Humidity,pH,Rainfall")

# Handle user messages
async def handle_message(update: Update, context: CallbackContext):
    try:
        values = list(map(float, update.message.text.split(",")))
        if len(values) != 7:
            await update.message.reply_text("❌ Invalid input! Send: N,P,K,Temperature,Humidity,pH,Rainfall")
            return

        crop = await get_crop_recommendation(*values)
        await update.message.reply_text(f"✅ Recommended Crop: {crop} 🌾")
    except:
        await update.message.reply_text("⚠️ Error! Send data in correct format.")

# Set up the bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Start the bot
print("✅ Telegram Bot is running...")
app.run_polling()
