import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# =========================================================
# CONFIG
# =========================================================

from config import BOT_TOKEN, ADMIN_ID


# =========================================================
# BOT
# =========================================================

BOT = Bot(token=BOT_TOKEN)
DP = Dispatcher()


# =========================================================
# PRIVATE GROUP
# =========================================================

PRIVATE_GROUP_ID = -1004441837503


# =========================================================
# QRIS
# =========================================================

QRIS_PATH = "assets/qris.jpg"


# =========================================================
# PAYMENT STATE
# =========================================================

PAYMENT_STATE_FILE = "payment_state.json"


# =========================================================
# ADMIN IDS
# =========================================================

if isinstance(ADMIN_ID, (list, tuple, set)):
    ADMIN_IDS = [int(x) for x in ADMIN_ID]
else:
    ADMIN_IDS = [int(ADMIN_ID)]


# =========================================================
# PACKAGE
# =========================================================

PACKAGE_MAP = {

    "1BLN": {
        "label": "1 Bulan",
        "price": 99000,
        "days": 30
    }

}


# =========================================================
# PAYMENT STATE
# =========================================================

def load_payment_state():

    if not os.path.exists(PAYMENT_STATE_FILE):
        return {}

    try:

        with open(
            PAYMENT_STATE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:

        print(
            "[PAYMENT STATE LOAD ERROR]",
            e
        )

        return {}


pending_payments = load_payment_state()


def save_payment_state():

    try:

        with open(
            PAYMENT_STATE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                pending_payments,
                f,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception as e:

        print(
            "[PAYMENT STATE SAVE ERROR]",
            e
        )

        return False


# =========================================================
# FORMAT RUPIAH
# =========================================================

def format_rupiah(value):

    try:

        return (
            f"Rp{int(value):,}"
            .replace(",", ".")
        )

    except Exception:

        return str(value)


# =========================================================
# START KEYBOARD
# =========================================================

def start_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="💳 BAYAR SEKARANG — Rp99.000",
                    callback_data="pay_1BLN"
                )
            ]

        ]
    )


# =========================================================
# ADMIN PAYMENT KEYBOARD
# =========================================================

def admin_payment_keyboard(user_id):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [

                InlineKeyboardButton(
                    text="✅ TERIMA",
                    callback_data=f"approve_{user_id}"
                ),

                InlineKeyboardButton(
                    text="❌ TOLAK",
                    callback_data=f"reject_{user_id}"
                )

            ]

        ]
    )


# =========================================================
# CHECK ADMIN
# =========================================================

async def is_authorized_admin(user_id):

    try:

        user_id = int(user_id)

        # Admin dari config
        if user_id in ADMIN_IDS:
            return True

        # Cek admin grup
        member = await BOT.get_chat_member(
            chat_id=PRIVATE_GROUP_ID,
            user_id=user_id
        )

        if member.status in (
            "administrator",
            "creator"
        ):
            return True

    except Exception as e:

        print(
            "[ADMIN CHECK ERROR]",
            e
        )

    return False


# =========================================================
# CREATE ONE-TIME INVITE
# =========================================================

async def create_one_time_invite_link():

    try:

        invite = await BOT.create_chat_invite_link(

            chat_id=PRIVATE_GROUP_ID,

            member_limit=1

        )

        print(
            "[INVITE CREATED]",
            invite.invite_link
        )

        return invite.invite_link

    except Exception as e:

        print(
            "[INVITE LINK ERROR]",
            e
        )

        return None


# =========================================================
# START
# =========================================================

@DP.message(CommandStart())
async def start_handler(message: Message):

    user = message.from_user

    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    print(
        f"[START] "
        f"{user_id} "
        f"@{username}"
    )

    # Simpan data awal transaksi
    pending_payments[str(user_id)] = {

        "telegram_id": user_id,

        "username": username,

        "nama": full_name,

        "package": "1BLN",

        "harga": 99000,

        "days": 30,

        "status": "STARTED",

        "created_at": datetime.now().isoformat()

    }

    save_payment_state()

    # =====================================================
    # WELCOME
    # =====================================================

    text = (

        "👋 <b>HALO, SELAMAT DATANG!</b>\n\n"

        "🤖 <b>PRO SIGNAL FX</b>\n\n"

        "Selamat datang di komunitas "
        "<b>PRO SIGNAL FX</b> — "
        "Private Forex Signal berbasis <b>AI</b>.\n\n"

        "📊 Analisis market berbasis AI\n"
        "🎯 Signal Forex\n"
        "⚡ Market Intelligence\n"
        "🧠 AI-Powered Analysis\n"
        "📈 Cocok untuk berbagai broker\n\n"

        "💎 <b>AKSES PRIVATE GROUP</b>\n\n"

        "💰 Harga hanya <b>Rp99.000</b>\n"
        "📅 Masa aktif <b>1 Bulan</b>\n"
        "🏦 <b>Bebas menggunakan broker apa saja</b>\n\n"

        "Untuk masuk ke grup <b>PRO SIGNAL FX</b>, "
        "cukup lakukan pembayaran sebesar "
        "<b>Rp99.000</b>.\n\n"

        "Klik tombol di bawah untuk melakukan pembayaran 👇"

    )

    await message.answer(

        text,

        reply_markup=start_keyboard(),

        parse_mode="HTML"

    )


# =========================================================
# PAYMENT BUTTON
# =========================================================

@DP.callback_query(F.data == "pay_1BLN")
async def payment_button(callback: CallbackQuery):

    user_id = callback.from_user.id

    package = PACKAGE_MAP["1BLN"]

    # Update state
    existing = pending_payments.get(
        str(user_id),
        {}
    )

    pending_payments[str(user_id)] = {

        "telegram_id": user_id,

        "username": callback.from_user.username or "",

        "nama": callback.from_user.full_name or "",

        "package": "1BLN",

        "harga": package["price"],

        "days": package["days"],

        "status": "WAITING_PROOF",

        "created_at": existing.get(
            "created_at",
            datetime.now().isoformat()
        )

    }

    save_payment_state()

    # =====================================================
    # PAYMENT TEXT
    # =====================================================

    text = (

        "💳 <b>PEMBAYARAN PRO SIGNAL FX</b>\n\n"

        "📦 Paket: <b>1 Bulan</b>\n"
        "💰 Harga: <b>Rp99.000</b>\n\n"

        "Silakan lakukan pembayaran "
        "sebesar <b>Rp99.000</b> melalui QRIS "
        "di bawah ini.\n\n"

        "📸 <b>Setelah pembayaran berhasil:</b>\n\n"

        "1️⃣ Screenshot bukti pembayaran\n"
        "2️⃣ Kirim screenshot tersebut "
        "ke bot ini\n"
        "3️⃣ Tunggu proses verifikasi admin\n\n"

        "👇 <b>KIRIM SS BUKTI PEMBAYARAN KE SINI YA</b>\n\n"

        "Setelah pembayaran diverifikasi, "
        "kamu akan mendapatkan <b>link invite "
        "private group PRO SIGNAL FX</b>."

    )

    if os.path.exists(QRIS_PATH):

        await BOT.send_photo(

            chat_id=user_id,

            photo=FSInputFile(QRIS_PATH),

            caption=text,

            parse_mode="HTML"

        )

    else:

        await BOT.send_message(

            chat_id=user_id,

            text=text,

            parse_mode="HTML"

        )

        print(
            "[QRIS ERROR] File tidak ditemukan:",
            QRIS_PATH
        )

    await callback.answer(
        "Silakan lakukan pembayaran Rp99.000."
    )


# =========================================================
# RECEIVE PAYMENT PROOF
# =========================================================

@DP.message(F.photo)
async def payment_proof_handler(message: Message):

    user_id = message.from_user.id

    username = message.from_user.username or ""

    full_name = message.from_user.full_name or ""

    payment = pending_payments.get(
        str(user_id)
    )

    # =====================================================
    # BELUM MULAI TRANSAKSI
    # =====================================================

    if not payment:

        await message.answer(

            "❌ <b>Belum ada pembayaran aktif.</b>\n\n"

            "Silakan tekan /start terlebih dahulu "
            "untuk melakukan pendaftaran.",

            parse_mode="HTML"

        )

        return

    # =====================================================
    # CEK STATUS
    # =====================================================

    status = payment.get(
        "status",
        ""
    )

    if status == "APPROVED":

        await message.answer(

            "✅ Pembayaran kamu sudah disetujui.\n\n"
            "Silakan gunakan link invite "
            "yang sebelumnya sudah diberikan."

        )

        return

    if status == "WAITING_ADMIN":

        await message.answer(

            "⏳ Bukti pembayaran kamu sudah diterima.\n\n"
            "Saat ini masih menunggu verifikasi admin."

        )

        return

    if status not in (
        "WAITING_PROOF",
        "STARTED"
    ):

        await message.answer(

            "⚠️ Status pembayaran kamu saat ini: "
            f"<b>{status}</b>",

            parse_mode="HTML"

        )

        return

    # =====================================================
    # SAVE PROOF
    # =====================================================

    photo = message.photo[-1]

    proof_file_id = photo.file_id

    payment["telegram_id"] = user_id

    payment["username"] = username

    payment["nama"] = full_name

    payment["proof_file_id"] = proof_file_id

    payment["proof_time"] = datetime.now().isoformat()

    payment["status"] = "WAITING_ADMIN"

    save_payment_state()

    print(
        f"[PAYMENT PROOF] "
        f"{user_id} "
        f"@{username}"
    )

    # =====================================================
    # SEND PROOF TO GROUP
    # =====================================================

    admin_caption = (

        "💳 <b>PEMBAYARAN BARU</b>\n\n"

        "👤 <b>DATA USER</b>\n"
        f"Nama: <b>{full_name}</b>\n"
        f"Username: @{username if username else '-'}\n"
        f"Telegram ID: <code>{user_id}</code>\n\n"

        "📦 <b>PAKET</b>\n"
        "1 Bulan\n"
        "💰 Harga: <b>Rp99.000</b>\n\n"

        "📋 Status: <b>MENUNGGU VERIFIKASI</b>\n\n"

        "Silakan periksa bukti pembayaran "
        "kemudian pilih tombol di bawah."

    )

    keyboard = admin_payment_keyboard(
        user_id
    )

    try:

        await BOT.send_photo(

            chat_id=PRIVATE_GROUP_ID,

            photo=proof_file_id,

            caption=admin_caption,

            reply_markup=keyboard,

            parse_mode="HTML"

        )

        print(
            "[PAYMENT SENT TO GROUP]",
            PRIVATE_GROUP_ID
        )

    except Exception as e:

        print(
            "[SEND PAYMENT TO GROUP ERROR]",
            e
        )

        payment["status"] = "WAITING_PROOF"

        save_payment_state()

        await message.answer(

            "⚠️ Bukti pembayaran sudah diterima, "
            "tetapi gagal diteruskan ke admin.\n\n"

            "Silakan coba kirim kembali "
            "beberapa saat lagi."

        )

        return

    # =====================================================
    # USER CONFIRMATION
    # =====================================================

    await message.answer(

        "✅ <b>BUKTI PEMBAYARAN DITERIMA</b>\n\n"

        "Bukti pembayaran kamu sudah "
        "diteruskan ke admin untuk diverifikasi.\n\n"

        "⏳ Mohon tunggu proses verifikasi.\n\n"

        "Jika pembayaran disetujui, "
        "bot akan otomatis mengirimkan "
        "link invite private group "
        "<b>PRO SIGNAL FX</b>.",

        parse_mode="HTML"

    )


# =========================================================
# APPROVE PAYMENT
# =========================================================

@DP.callback_query(F.data.startswith("approve_"))
async def approve_payment(
    callback: CallbackQuery
):

    admin_id = callback.from_user.id

    # =====================================================
    # CHECK ADMIN
    # =====================================================

    authorized = await is_authorized_admin(
        admin_id
    )

    if not authorized:

        await callback.answer(

            "❌ Kamu tidak memiliki akses.",

            show_alert=True

        )

        return

    # =====================================================
    # GET USER ID
    # =====================================================

    try:

        user_id = int(
            callback.data.replace(
                "approve_",
                "",
                1
            )
        )

    except Exception:

        await callback.answer(

            "❌ User ID tidak valid.",

            show_alert=True

        )

        return

    payment = pending_payments.get(
        str(user_id)
    )

    if not payment:

        await callback.answer(

            "❌ Data pembayaran tidak ditemukan.",

            show_alert=True

        )

        return

    # =====================================================
    # CHECK STATUS
    # =====================================================

    if payment.get("status") == "APPROVED":

        await callback.answer(

            "Pembayaran sudah disetujui.",

            show_alert=True

        )

        return

    if payment.get("status") != "WAITING_ADMIN":

        await callback.answer(

            "Pembayaran belum menunggu verifikasi.",

            show_alert=True

        )

        return

    # =====================================================
    # CREATE INVITE
    # =====================================================

    invite_link = await create_one_time_invite_link()

    if not invite_link:

        await callback.answer(

            "❌ Gagal membuat invite link.",

            show_alert=True

        )

        return

    # =====================================================
    # UPDATE STATE
    # =====================================================

    payment["status"] = "APPROVED"

    payment["approved_at"] = (
        datetime.now().isoformat()
    )

    payment["approved_by"] = admin_id

    payment["invite_link"] = invite_link

    save_payment_state()

    # =====================================================
    # SEND INVITE TO USER
    # =====================================================

    user_text = (

        "🎉 <b>PEMBAYARAN BERHASIL!</b>\n\n"

        "Selamat, pembayaran kamu sebesar "
        "<b>Rp99.000</b> telah disetujui.\n\n"

        "🤖 Selamat datang di "
        "<b>PRO SIGNAL FX</b>\n\n"

        "🔐 <b>PRIVATE GROUP</b>\n\n"

        "Silakan klik link di bawah untuk "
        "bergabung ke private group:\n\n"

        f"👉 {invite_link}\n\n"

        "⚠️ <b>PENTING</b>\n"
        "Link ini hanya dapat digunakan "
        "untuk <b>1 member</b>.\n\n"

        "Jangan bagikan link ini kepada orang lain.\n\n"

        "Selamat bergabung di "
        "<b>PRO SIGNAL FX</b> 🚀"

    )

    try:

        await BOT.send_message(

            chat_id=user_id,

            text=user_text,

            parse_mode="HTML"

        )

        print(
            "[INVITE SENT TO USER]",
            user_id
        )

    except Exception as e:

        print(
            "[SEND INVITE USER ERROR]",
            e
        )

    # =====================================================
    # UPDATE GROUP MESSAGE
    # =====================================================

    try:

        await callback.message.edit_caption(

            caption=(

                "✅ <b>PAYMENT APPROVED</b>\n\n"

                f"👤 User: <code>{user_id}</code>\n"

                f"📦 Paket: <b>1 Bulan</b>\n"

                "💰 Harga: <b>Rp99.000</b>\n\n"

                "📋 Status: <b>APPROVED</b>\n"

                "🔐 Invite: <b>CREATED</b>\n\n"

                "Link invite sekali pakai "
                "telah dikirim ke user."

            ),

            parse_mode="HTML",

            reply_markup=None

        )

    except Exception as e:

        print(
            "[EDIT GROUP MESSAGE ERROR]",
            e
        )

    await callback.answer(
        "✅ Pembayaran diterima."
    )


# =========================================================
# REJECT PAYMENT
# =========================================================

@DP.callback_query(F.data.startswith("reject_"))
async def reject_payment(
    callback: CallbackQuery
):

    admin_id = callback.from_user.id

    # =====================================================
    # CHECK ADMIN
    # =====================================================

    authorized = await is_authorized_admin(
        admin_id
    )

    if not authorized:

        await callback.answer(

            "❌ Kamu tidak memiliki akses.",

            show_alert=True

        )

        return

    # =====================================================
    # GET USER ID
    # =====================================================

    try:

        user_id = int(
            callback.data.replace(
                "reject_",
                "",
                1
            )
        )

    except Exception:

        await callback.answer(

            "❌ User ID tidak valid.",

            show_alert=True

        )

        return

    payment = pending_payments.get(
        str(user_id)
    )

    if not payment:

        await callback.answer(

            "❌ Data pembayaran tidak ditemukan.",

            show_alert=True

        )

        return

    # =====================================================
    # UPDATE STATE
    # =====================================================

    payment["status"] = "REJECTED"

    payment["rejected_at"] = (
        datetime.now().isoformat()
    )

    payment["rejected_by"] = admin_id

    save_payment_state()

    # =====================================================
    # SEND REJECTION TO USER
    # =====================================================

    try:

        await BOT.send_message(

            chat_id=user_id,

            text=(

                "❌ <b>PEMBAYARAN GAGAL</b>\n\n"

                "Maaf, pembayaran kamu "
                "belum dapat diverifikasi "
                "oleh admin.\n\n"

                "Silakan hubungi admin kami "
                "untuk informasi lebih lanjut:\n\n"

                "👉 <b>@ProSignals_FX11</b>"

            ),

            parse_mode="HTML"

        )

        print(
            "[REJECT SENT TO USER]",
            user_id
        )

    except Exception as e:

        print(
            "[SEND REJECT ERROR]",
            e
        )

    # =====================================================
    # UPDATE GROUP MESSAGE
    # =====================================================

    try:

        await callback.message.edit_caption(

            caption=(

                "❌ <b>PAYMENT REJECTED</b>\n\n"

                f"👤 User: <code>{user_id}</code>\n"

                "📦 Paket: <b>1 Bulan</b>\n"

                "💰 Harga: <b>Rp99.000</b>\n\n"

                "📋 Status: <b>REJECTED</b>\n\n"

                "User telah diberitahu untuk "
                "menghubungi @ProSignals_FX11."

            ),

            parse_mode="HTML",

            reply_markup=None

        )

    except Exception as e:

        print(
            "[EDIT REJECT MESSAGE ERROR]",
            e
        )

    await callback.answer(
        "❌ Pembayaran ditolak."
    )


# =========================================================
# ERROR HANDLER
# =========================================================

@DP.errors()
async def global_error_handler(event):

    print(
        "[BOT ERROR]",
        event.exception
    )


# =========================================================
# MAIN
# =========================================================

async def main():

    print(
        "=========================================="
    )

    print(
        "🤖 PRO SIGNAL FX BOT STARTING..."
    )

    print(
        "=========================================="
    )

    print(
        "PRIVATE GROUP:",
        PRIVATE_GROUP_ID
    )

    print(
        "ADMIN IDS:",
        ADMIN_IDS
    )

    print(
        "QRIS PATH:",
        QRIS_PATH
    )

    print("")
    print("PACKAGE:")
    print(" - 1 BULAN : Rp99.000")

    print("")
    print("FLOW:")
    print(" - /start")
    print(" - Welcome PRO SIGNAL FX")
    print(" - Bayar Rp99.000")
    print(" - Kirim bukti pembayaran")
    print(" - Bukti masuk ke private group")
    print(" - Admin TERIMA / TOLAK")
    print(" - APPROVE = One Time Invite")
    print(" - REJECT = Hubungi @ProSignals_FX11")

    print(
        "=========================================="
    )

    try:

        await DP.start_polling(
            BOT
        )

    finally:

        await BOT.session.close()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
