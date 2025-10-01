import instaloader
import requests
from telebot import TeleBot
from io import BytesIO

TOKEN = "8270329793:AAGY6su9qUwgsMCArCjsap3n5e8YW8LvDaY"
bot = TeleBot(TOKEN)
ADMIN_USERNAME = "mahdiraofi"

users_list = []

L = instaloader.Instaloader(download_pictures=False, download_videos=False)

L.context._session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
})

user_states = {}

@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    user_states[chat_id] = None
    username = message.from_user.username

    # پیام خوشامدگویی
    welcome_msg = (
        "🌱 به ربات دانلودر اینستاگرام خوش آمدید!\n\n"
        "این ربات به شما امکان می‌دهد تا محتوای اینستاگرام را دانلود کنید.\n\n"
        "📌 قابلیت‌ها:\n"
        "1️⃣ دانلود پست‌ها و ریلزهای اینستاگرام با لینک آن‌ها \n"
        "2️⃣ دانلود عکس پروفایل و اطلاعات کاربران با یوزرنیم \n\n"
        "⚠️ توجه:\n"
        "- برای استفاده از هر قابلیت، ابتدا دستور مربوطه را انتخاب کنید.\n\n"
        "🎯 استفاده:\n"
        "برای دانلود با لینک، روی /link کلیک کنید.\n"
        "برای دانلود پروفایل با یوزرنیم، روی /profile کلیک کنید.\n\n"
        "💡 نکته: هر زمان می‌خواهید به صفحه اصلی بازگردید، کافی است /start بزنید."
    )

    if not any(u["chat_id"] == chat_id for u in users_list):
        users_list.append({"chat_id": chat_id, "username": username})

    if username == ADMIN_USERNAME:
        admin_msg = (
            "\n🔑 دستورات ویژه ادمین:\n"
            "1️⃣ /user - مشاهده لیست کاربران ربات\n"
            "2️⃣ /broadcast - ارسال پیام به همه کاربران"
        )
        welcome_msg += admin_msg

    bot.send_message(chat_id, welcome_msg)

# ادامه کد بدون تغییر
@bot.message_handler(commands=["link"])
def set_link_mode(message):
    user_states[message.chat.id] = "link"
    link_msg = (
        "🔗لطفاً لینک پست یا ریلز مدنظر خود را ارسال کنید.\n\n"
        "💡 نکات مهم:\n"
        "1️⃣ فقط لینک‌های پست و ریلز اینستاگرام پشتیبانی می‌شوند.\n"
        "2️⃣ بعد از ارسال لینک، ربات ویدیو یا عکس را مستقیم به تلگرام شما می‌فرستد.\n"
        "3️⃣ برای دانلود پست یا ریلز دیگری، می‌توانید دوباره لینک جدید ارسال کنید.\n\n"
        "🏠 برای برگشت به منوی اصلی همیشه می‌توانید /start بزنید."
    )
    bot.send_message(message.chat.id, link_msg)

@bot.message_handler(commands=["profile"])
def set_profile_mode(message):
    user_states[message.chat.id] = "profile"
    profile_msg = (
        "🔗لطفاً یوزرنیم کاربری که می‌خواهید پروفایلش را ببینید ارسال کنید.\n\n"
        "💡 نکات مهم:\n"
        "1️⃣ ربات عکس پروفایل، بیو، تعداد فالوورها و فالووینگ، تعداد پست‌ها و وضعیت عمومی/خصوصی پیج را نمایش می‌دهد.\n"
        "2️⃣ اگر یوزرنیم اشتباه باشد، ربات خطا می‌دهد.\n"
        "3️⃣ بعد از ارسال یوزرنیم، برای دانلود پروفایل دیگری می‌توانید دوباره یوزرنیم جدید ارسال کنید.\n"
        "   مثال: cristiano\n\n"
        "🏠 برای برگشت به منوی اصلی همیشه می‌توانید /start بزنید."
    )
    bot.send_message(message.chat.id, profile_msg)

def is_admin(message):
    return message.from_user.username == ADMIN_USERNAME

@bot.message_handler(commands=["user"])
def show_stats(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "⚠️ فقط ادمین قادر به استفاده از این کامند است")
        return
    bot.send_message(message.chat.id, f"📊 تعداد کاربران فعال: {len(users_list)}")

def list_users(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "⚠️ فقط ادمین قادر به استفاده از این کامند است")
        return
    if users_list:
        user_list_text = "\n".join([u["username"] or "بدون یوزرنیم" for u in users_list])
        bot.send_message(message.chat.id, f"👥 لیست کاربران:\n{user_list_text}")
    else:
        bot.send_message(message.chat.id, "❌ هیچ کاربری هنوز ربات را استارت نکرده است")

@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
    if not is_admin(message):
        bot.send_message(message.chat.id, "⚠️ فقط ادمین قادر به استفاده از این کامند است")
        return
    bot.send_message(message.chat.id, "📢 لطفاً پیام خود را ارسال کنید تا برای همه کاربران ارسال شود")

    @bot.message_handler(func=lambda m: True, content_types=['text'])
    def send_broadcast(m):
        text_to_send = m.text
        for u in users_list:
            try:
                bot.send_message(u["chat_id"], f"📢 پیام ادمین:\n\n{text_to_send}")
            except:
                continue
        bot.send_message(message.chat.id, "✅ پیام برای همه کاربران ارسال شد")
        bot.register_next_step_handler(message, lambda msg: None)

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_states or user_states[chat_id] is None:
        bot.send_message(chat_id, "⚠️ ابتدا /start بزنید")
        return

    if user_states[chat_id] == "link":
        bot.send_message(chat_id, "⏳")
        try:
            if "/stories/" in text or "/highlight/" in text:
                bot.send_message(chat_id, "⚠️ شما قادر به استفاده از این قابلیت برای استوری یا هایلایت نیستید")
                return

            shortcode = text.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)

            caption = f"👤: {post.owner_username}\n📝: {post.caption or 'none'}\n\n"

            if post.is_video:
                url = post.video_url
                file = BytesIO(requests.get(url).content)
                file.name = f"{post.shortcode}.mp4"
                bot.send_video(chat_id, video=file, caption=caption)
                bot.send_message(chat_id,"برای دانلود دوباره می‌توانید لینک دیگری ارسال کنید یا برای برگشت به خانه روی /start بزنید")
            else:
                if post.typename == "GraphSidecar":
                    for i, res in enumerate(post.get_sidecar_nodes(), start=1):
                        url = res.video_url if res.is_video else res.display_url
                        file = BytesIO(requests.get(url).content)
                        file.name = f"{post.shortcode}_{i}.{'mp4' if res.is_video else 'jpg'}"
                        if res.is_video:
                            bot.send_video(chat_id, video=file)
                        else:
                            bot.send_photo(chat_id, photo=file)
                    bot.send_message(chat_id, caption)
                    bot.send_message(chat_id, "برای دانلود دوباره می‌توانید لینک دیگری ارسال کنید یا برای برگشت به خانه روی /start بزنید")

                else:
                    url = post.url
                    file = BytesIO(requests.get(url).content)
                    file.name = f"{post.shortcode}.jpg"
                    bot.send_photo(chat_id, photo=file, caption=caption)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطا: {e}")

    elif user_states[chat_id] == "profile":
        bot.send_message(chat_id, "⏳")
        try:
            profile = instaloader.Profile.from_username(L.context, text)
            url = profile.profile_pic_url
            file = BytesIO(requests.get(url).content)
            file.name = f"{profile.username}_profile.jpg"

            caption = (
                f"👤Username: {profile.username}\n"
                f"📝Bio: {profile.biography or '---'}\n"
                f"👥Follower: {profile.followers}\n"
                f"👤Following: {profile.followees}\n"
                f"📸Number of posts: {profile.mediacount}\n"
                f"🔒Status: {'Private' if profile.is_private else 'Public'}\n\n"
            )

            bot.send_photo(chat_id, photo=file, caption=caption)
            bot.send_message(chat_id,"برای دانلود دوباره پروفایل، یوزرنیم دیگری ارسال کنید یا برای برگشت به خانه روی /start بزنید")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطا: {e}")

bot.infinity_polling()
