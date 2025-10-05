import os
import instaloader
import requests
import telebot
from instagrapi import Client
from io import BytesIO
from flask import Flask, request

TOKEN = "7672565477:AAEPJ_cardvE_eZ1d8bz_koY5sx5hAMl8MY"
ADMIN_USERNAME = "mahdiraofi"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
SESSION_FILE = "settings.json"
IG_USERNAME = "mahditest55"
IG_PASSWORD = "MohammadMahdi1389"

L = instaloader.Instaloader(download_pictures=False, download_videos=False)
L.context._session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
})
cl = Client()
if os.path.exists(SESSION_FILE):
    cl.load_settings(SESSION_FILE)
else:
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.dump_settings(SESSION_FILE)

users_list = []
user_states = {}

@bot.message_handler(commands=["start"])
def start_message(message):
    chat_id = message.chat.id
    username = message.from_user.username or ""

    if chat_id not in [u["chat_id"] for u in users_list]:
        users_list.append({"chat_id": chat_id, "username": username})

    welcome_msg = (
        "🌱 به ربات InstaZip خوش آمدید!\n\n"
        "این ربات به شما امکان می‌دهد تا محتوای اینستاگرام را دانلود کنید.\n\n"
        "📌 قابلیت‌ها:\n"
        "1️⃣ دانلود پست‌ها ، ریلزها اینستاگرام با لینک آن‌ها \n"
        "2️⃣دانلود عکس پروفایل و اطلاعات کاربران با یوزرنیم\n\n"
        "⚠️ توجه:\n"
        "- برای استفاده از هر قابلیت، ابتدا دستور مربوطه را انتخاب کنید.\n\n"
        "🎯 استفاده:\n"
        "برای دانلود با لینک، روی /link کلیک کنید.\n"
        "برای دانلود پروفایل با یوزرنیم، روی /profile کلیک کنید.\n\n"
        "💡 نکته: هر زمان می‌خواهید به صفحه اصلی بازگردید، کافی است /start بزنید."
    )

    if username.lower() == ADMIN_USERNAME.lower():
        welcome_msg += (
            "\n\n🔑 دستورات ویژه ادمین:\n"
            "/user - مشاهده لیست کاربران\n"
            "/login - پاک کردن فایل سشن و ورود مجدد"
        )

    bot.send_message(chat_id, welcome_msg)


def is_admin(message):
    return message.from_user.username == ADMIN_USERNAME

@bot.message_handler(commands=["user"])
def show_users(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "⚠️ فقط ادمین قادر به استفاده از این کامند است.")
        return
    if users_list:
        text = "\n".join([u["username"] for u in users_list])
        bot.send_message(message.chat.id, f"👥 کاربران:\n{text}")
    else:
        bot.send_message(message.chat.id, "❌ هیچ کاربری هنوز ربات را استارت نکرده است.")

@bot.message_handler(commands=["login"])
def admin_login(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "⚠️ فقط ادمین قادر به استفاده از این کامند است.")
        return
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    try:
        cl.login(IG_USERNAME, IG_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        bot.send_message(message.chat.id, "✅ ورود مجدد موفقیت‌آمیز انجام شد و سشن جدید ساخته شد.")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ خطا در ورود مجدد: {e}")

@bot.message_handler(commands=["link"])
def link_command(message):
    chat_id = message.chat.id
    user_states[chat_id] = "link"
    link_msg = (
        "🔗لطفاً لینک پست یا ریلز مدنظر خود را ارسال کنید.\n\n"
        "💡 نکات مهم:\n"
        "1️⃣ فقط لینک‌های پست و ریلز اینستاگرام پشتیبانی می‌شوند.\n"
        "2️⃣ بعد از ارسال لینک، ربات ویدیو یا عکس را مستقیم به تلگرام شما می‌فرستد.\n"
        "3️⃣ برای دانلود پست یا ریلز دیگری، می‌توانید دوباره لینک جدید ارسال کنید.\n\n"
        "🏠 برای برگشت به منوی اصلی همیشه می‌توانید /start بزنید."
    )
    bot.send_message(chat_id, link_msg)

@bot.message_handler(commands=["profile"])
def profile_command(message):
    chat_id = message.chat.id
    user_states[chat_id] = "profile"
    profile_msg = (
        "🔗لطفاً یوزرنیم کاربری که می‌خواهید پروفایلش را ببینید ارسال کنید.\n\n"
        "💡 نکات مهم:\n"
        "1️⃣ ربات عکس پروفایل، بیو، تعداد فالوورها و فالووینگ، تعداد پست‌ها و وضعیت عمومی/خصوصی پیج را نمایش می‌دهد.\n"
        "2️⃣ اگر یوزرنیم اشتباه باشد، ربات خطا می‌دهد.\n"
        "3️⃣ بعد از ارسال یوزرنیم، برای دانلود پروفایل دیگری می‌توانید دوباره یوزرنیم جدید ارسال کنید.\n"
        "   مثال: cristiano\n\n"
        "🏠 برای برگشت به منوی اصلی همیشه می‌توانید /start بزنید."
    )
    bot.send_message(chat_id, profile_msg)
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_states or user_states[chat_id] is None:
        bot.send_message(chat_id, "⚠️ ابتدا یکی از کامندهای /link, /profile یا /story را انتخاب کنید.")
        return

    bot.send_message(chat_id, "⏳")

    state = user_states[chat_id]
    if state == "link":
        try:
            shortcode = text.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            media_files = []
            if post.typename == "GraphSidecar":
                for node in post.get_sidecar_nodes():
                    url = node.video_url if node.is_video else node.display_url
                    media_files.append((url, node.is_video))
            else:
                url = post.video_url if post.is_video else post.url
                media_files.append((url, post.is_video))

            for idx, (url, is_video) in enumerate(media_files):
                file = BytesIO(requests.get(url).content)
                file.name = f"{shortcode}_{idx}.{'mp4' if is_video else 'jpg'}"
                file.seek(0)
                if is_video:
                    bot.send_video(chat_id, video=file, caption=post.caption if idx == len(media_files)-1 else "")
                else:
                    bot.send_photo(chat_id, photo=file, caption=post.caption if idx == len(media_files)-1 else "")
            bot.send_message(chat_id,"برای دانلود دوباره می‌توانید لینک دیگری ارسال کنید یا برای برگشت به خانه روی /start بزنید")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️خطا در دانلود محتوا")

    elif state == "profile":
        try:
            profile = instaloader.Profile.from_username(L.context, text)
            file = BytesIO(requests.get(profile.profile_pic_url).content)
            file.name = f"{profile.username}_profile.jpg"
            file.seek(0)
            caption = (
                f"👤 Username: {profile.username}\n"
                f"📝 Bio: {profile.biography or '---'}\n"
                f"👥 Followers: {profile.followers}\n"
                f"👤 Following: {profile.followees}\n"
                f"📸 Posts: {profile.mediacount}\n"
                f"🔒 Status: {'Private' if profile.is_private else 'Public'}"
            )
            bot.send_photo(chat_id, photo=file, caption=caption)
            bot.send_message(chat_id, "برای دانلود دوباره پروفایل، یوزرنیم دیگری ارسال کنید یا برای برگشت به خانه روی /start بزنید")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطا در دانلود پروفایل")
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200
@app.route('/')
def index():
    return "Bot is running!"


if __name__ == '__main__':
    app.run()
