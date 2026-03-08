import os
import asyncio
import base64
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()

# Validate environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")  # Default to Opus 4.6

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# Configure Anthropic client with custom base URL if provided
if ANTHROPIC_BASE_URL:
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
else:
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


# Store conversation history for each user
conversation_history = {}

# Store user statistics
user_stats = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🤖 Welcome to ClawdChat!\n\n"
        "I'm an AI assistant powered by Claude. "
        "You can chat with me about anything!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help message\n"
        "/reset - Reset conversation context"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 ClawdChat Help\n\n"
        "I can help you with:\n"
        "• 💬 Answer questions\n"
        "• 📝 Write code\n"
        "• 🔍 Analyze images\n"
        "• 📄 Read documents\n"
        "• 💡 Have conversations\n\n"
        "Features:\n"
        "• 📸 Send photos for analysis\n"
        "• 📎 Upload text files & documents\n"
        "• 🎤 Voice messages (info only)\n"
        "• 📍 Share locations\n"
        "• 😀 Send stickers\n"
        "• 💾 Conversation memory\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/reset - Clear conversation\n"
        "/stats - View your statistics\n"
        "/id - Get your User & Chat IDs\n"
        "/about - About this bot"
    )
    await update.message.reply_text(help_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation context."""
    user_id = update.effective_user.id
    if user_id in conversation_history:
        del conversation_history[user_id]
    await update.message.reply_text("🔄 Conversation context reset! How can I help you?")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user statistics."""
    user_id = update.effective_user.id

    if user_id not in user_stats:
        user_stats[user_id] = {
            "messages_sent": 0,
            "photos_sent": 0,
            "documents_sent": 0,
            "first_interaction": datetime.now().isoformat()
        }

    stats = user_stats[user_id]
    stats_text = (
        f"📊 Your Statistics\n\n"
        f"Messages sent: {stats['messages_sent']}\n"
        f"Photos sent: {stats['photos_sent']}\n"
        f"Documents sent: {stats['documents_sent']}\n"
        f"First interaction: {stats['first_interaction'][:10]}"
    )
    await update.message.reply_text(stats_text)


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user and chat IDs."""
    user = update.effective_user
    chat = update.effective_chat

    id_text = (
        f"🆔 Identification\n\n"
        f"Your User ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'N/A'}\n"
        f"Chat ID: {chat.id}\n"
        f"Chat Type: {chat.type}"
    )
    await update.message.reply_text(id_text)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show information about the bot."""
    about_text = (
        "🤖 About ClawdChat\n\n"
        "Version: 1.0.0\n\n"
        "A powerful Telegram bot powered by Claude AI.\n\n"
        "Features:\n"
        "• 💬 Natural conversations\n"
        "• 📸 Image analysis\n"
        "• 📄 Document processing\n"
        "• 💾 Conversation memory\n\n"
        "Powered by Anthropic Claude"
    )
    await update.message.reply_text(about_text)


def update_user_stats(user_id, message_type):
    """Update user statistics."""
    if user_id not in user_stats:
        user_stats[user_id] = {
            "messages_sent": 0,
            "photos_sent": 0,
            "documents_sent": 0,
            "voice_messages": 0,
            "videos_sent": 0,
            "first_interaction": datetime.now().isoformat()
        }

    user_stats[user_id][f"{message_type}_sent"] = user_stats[user_id].get(f"{message_type}_sent", 0) + 1


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and get responses from Claude."""
    user_message = update.message.text
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "messages")

        # Send typing action
        await update.message.chat.send_action("typing")

        # Get or create conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Add user message to history
        conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })

        # Keep last 10 messages for context
        messages = conversation_history[user_id][-10:]

        # Call Claude API
        response = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system="You are a helpful AI assistant for a Telegram bot called ClawdChat. Be concise, friendly, and helpful. Use emojis when appropriate.",
            messages=messages
        )

        # Extract response text (handle different content block types)
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break
            # Skip thinking blocks and other block types

        if not response_text:
            raise Exception("No text response received from API")

        # Add assistant response to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": response_text
        })

        # Keep only last 20 messages
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        # Send response (handle long messages)
        if len(response_text) > 4000:
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}\n\nPlease try again later."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages with vision support."""
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "photos")

        # Send typing action
        await update.message.chat.send_action("typing")

        # Get the largest photo (best quality)
        photo = update.message.photo[-1]
        file = await photo.get_file()

        # Download photo bytes
        photo_bytes = await file.download_as_bytearray()

        # Convert to base64
        photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')

        # Get caption if provided
        caption = update.message.caption or "What's in this image?"

        # Get or create conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Create message with image
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": photo_base64
                    }
                },
                {
                    "type": "text",
                    "text": caption
                }
            ]
        }

        # Add to history
        conversation_history[user_id].append(user_message)

        # Keep last 10 messages (images count as messages)
        messages = conversation_history[user_id][-10:]

        # Call Claude API with vision
        response = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system="You are a helpful AI assistant for a Telegram bot called ClawdChat with vision capabilities. Analyze images and provide helpful, concise responses. Use emojis when appropriate.",
            messages=messages
        )

        # Extract response text
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break

        if not response_text:
            raise Exception("No text response received from API")

        # Add assistant response to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": response_text
        })

        # Keep only last 20 messages
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        # Send response
        if len(response_text) > 4000:
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error processing photo: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Sorry, I couldn't process that image: {str(e)}\n\nPlease try again later."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document messages (PDF, text files, etc.)."""
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "documents")

        document = update.message.document
        file_name = document.file_name
        file_size = document.file_size

        # Check file size (limit to 10MB for now)
        if file_size and file_size > 10 * 1024 * 1024:
            await update.message.reply_text(
                "❌ File too large. Please send files under 10MB."
            )
            return

        # Send typing action
        await update.message.chat.send_action("typing")

        # Download file
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()

        # Try to read as text
        try:
            file_content = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            await update.message.reply_text(
                f"❌ I can only process text files and PDFs right now.\n\n"
                f"File: {file_name}\n"
                f"Size: {file_size / 1024:.1f} KB"
            )
            return

        # Get caption if provided
        caption = update.message.caption or f"Please analyze this file: {file_name}"

        # Get or create conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Add to history (truncate if too long)
        max_file_length = 100000  # Limit file content length
        if len(file_content) > max_file_length:
            file_content = file_content[:max_file_length] + "\n\n... (file truncated due to length)"

        user_message = {
            "role": "user",
            "content": f"{caption}\n\nFile content:\n{file_content}"
        }

        conversation_history[user_id].append(user_message)

        # Keep last 10 messages
        messages = conversation_history[user_id][-10:]

        # Call Claude API
        response = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4096,
            system="You are a helpful AI assistant for a Telegram bot called ClawdChat. Analyze documents and files, providing helpful insights. Be concise and use emojis when appropriate.",
            messages=messages
        )

        # Extract response text
        response_text = ""
        for block in response.content:
            if block.type == "text":
                response_text = block.text
                break

        if not response_text:
            raise Exception("No text response received from API")

        # Add assistant response to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": response_text
        })

        # Keep only last 20 messages
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        # Send response
        if len(response_text) > 4000:
            chunks = [response_text[i:i+4000] for i in range(0, len(response_text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(response_text)

    except Exception as e:
        print(f"Error processing document: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Sorry, I couldn't process that file: {str(e)}\n\nPlease try again later."
        )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "voice_messages")

        voice = update.message.voice
        duration = voice.duration
        file_size = voice.file_size

        # Download voice file
        file = await voice.get_file()
        voice_bytes = await file.download_as_bytearray()

        await update.message.reply_text(
            f"🎤 Voice message received!\n\n"
            f"Duration: {duration:.1f} seconds\n"
            f"Size: {file_size / 1024:.1f} KB\n\n"
            f"⚠️ Voice transcription is not available yet. "
            f"The bot would need a speech-to-text service to process voice messages.\n\n"
            f"You can:\n"
            f"• Type your message instead\n"
            f"• Send an image with what you want to ask"
        )

    except Exception as e:
        print(f"Error processing voice: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Sorry, I couldn't process that voice message: {str(e)}"
        )


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle video messages (video notes/round videos)."""
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "videos")

        video_note = update.message.video_note
        duration = video_note.duration
        file_size = video_note.file_size

        await update.message.reply_text(
            f"🎬 Video received!\n\n"
            f"Duration: {duration:.1f} seconds\n"
            f"Size: {file_size / 1024:.1f} KB\n\n"
            f"⚠️ Video analysis is not supported yet.\n\n"
            f"• For now, I can only analyze images and text\n"
            f"• You can describe what's in the video and I'll help analyze that"
        )

    except Exception as e:
        print(f"Error processing video: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}"
        )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular video messages."""
    user_id = update.effective_user.id

    try:
        # Update stats
        update_user_stats(user_id, "videos")

        video = update.message.video
        duration = video.duration
        file_size = video.file_size if video.file_size else 0

        await update.message.reply_text(
            f"🎬 Video received!\n\n"
            f"Duration: {duration:.1f} seconds\n"
            f"Size: {file_size / 1024:.1f} KB\n\n"
            f"⚠️ Video analysis is not supported yet.\n\n"
            f"• I can analyze images (send screenshots instead!)\n"
            f"• Or describe the video content and I'll help"
        )

    except Exception as e:
        print(f"Error processing video: {e}")
        await update.message.reply_text(
            f"❌ Sorry, I encountered an error: {str(e)}"
        )


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle sticker messages."""
    sticker = update.message.sticker
    set_name = sticker.set_name if hasattr(sticker, 'set_name') else "Unknown"

    await update.message.reply_text(
        f"😀 Sticker received!\n\n"
        f"Sticker Set: {set_name}\n"
        f"⚠️ I can't analyze stickers yet, but they're fun!\n\n"
        f"Feel free to send me images or text instead!"
    )


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle location messages."""
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude

    await update.message.reply_text(
        f"📍 Location received!\n\n"
        f"Latitude: {latitude:.4f}\n"
        f"Longitude: {longitude:.4f}\n\n"
        f"⚠️ I don't have location-based features yet.\n\n"
        f"• Tell me about the location and I can help!\n"
        f"• Example: 'What's the weather at {latitude:.2f}, {longitude:.2f}?'"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    print(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("about", about_command))

    # Register message handlers for different content types
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
