import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ======= আপনার তথ্য দিন ========
TELEGRAM_BOT_TOKEN = "8624200309:AAEzw5SmqszlPDDmih-dpU1tbBFLmwe-RIE"
IMGBB_API_KEY = "a8031e7b8e23253a9d2365e94d32a806"

# ======= দ্রুত আপলোড (কোয়ালিটি অপরিবর্তিত) ========
def upload_to_imgbb_fast(image_data):
    """কোয়ালিটি না কমিয়ে দ্রুত আপলোড"""
    url = "https://api.imgbb.com/1/upload"
    
    # ডাইরেক্ট আপলোড - কোন কম্প্রেশন নেই
    files = {
        'image': ('image.jpg', image_data, 'image/jpeg')
    }
    data = {
        'key': IMGBB_API_KEY
    }
    
    # টাইমআউট কমিয়ে দ্রুত রেসপন্স
    response = requests.post(url, data=data, files=files, timeout=15)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            return result['data']['url']
    return None

# ======= টেলিগ্রাম হ্যান্ডলার (অপটিমাইজড) ========
async def start(update: Update, context):
    await update.message.reply_text(
        "🚀 হ্যালো! আমি ইমেজ আপলোড বট\n\n"
        "📸 ছবি পাঠান → সাথে সাথে লিংক\n"
        "✨ কোয়ালিটি অপরিবর্তিত থাকবে\n"
        "⚡ দ্রুত আপলোড সিস্টেম"
    )

async def handle_photo(update: Update, context):
    # "টাইপিং..." ইন্ডিকেটর দেখাবে (দ্রুত রেসপন্সের জন্য)
    await update.message.chat.send_action(action="typing")
    
    # ছবি ডাউনলোড (সর্বোচ্চ রেজোলিউশন)
    photo_file = await update.message.photo[-1].get_file()
    
    # "আপলোড হচ্ছে..." মেসেজ
    status_msg = await update.message.reply_text("📤 আপলোড হচ্ছে...")
    
    # ডাউনলোড
    image_bytes = await photo_file.download_as_bytearray()
    
    # আপলোড
    link = upload_to_imgbb_fast(image_bytes)
    
    # স্ট্যাটাস মেসেজ ডিলিট
    await status_msg.delete()
    
    if link:
        await update.message.reply_text(
            f"✅ সফল!\n\n"
            f"🔗 {link}\n\n"
            f"💡 কপি করে শেয়ার করুন"
        )
    else:
        await update.message.reply_text(
            "❌ ব্যর্থ!\n"
            "আবার চেষ্টা করুন অথবা ছবি ছোট করুন"
        )

async def handle_document(update: Update, context):
    if update.message.document.mime_type.startswith('image/'):
        await update.message.chat.send_action(action="typing")
        
        status_msg = await update.message.reply_text("📤 আপলোড হচ্ছে...")
        
        doc_file = await update.message.document.get_file()
        image_bytes = await doc_file.download_as_bytearray()
        
        link = upload_to_imgbb_fast(image_bytes)
        
        await status_msg.delete()
        
        if link:
            await update.message.reply_text(f"✅ {link}")
        else:
            await update.message.reply_text("❌ ব্যর্থ")
    else:
        await update.message.reply_text("📸 শুধু ছবি পাঠান")

def main():
    # বট তৈরি
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # হ্যান্ডলার যোগ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    
    print("🚀 বট চালু (কোয়ালিটি: অপরিবর্তিত)")
    print("⚡ দ্রুত আপলোড মোড অন")
    app.run_polling()

if __name__ == "__main__":
    main()