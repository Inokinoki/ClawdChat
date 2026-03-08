import os
import asyncio
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
        "• Answer questions\n"
        "• Write code\n"
        "• Analyze text\n"
        "• Have conversations\n"
        "• And much more!\n\n"
        "Just send me a message and I'll respond!"
    )
    await update.message.reply_text(help_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation context."""
    user_id = update.effective_user.id
    if user_id in conversation_history:
        del conversation_history[user_id]
    await update.message.reply_text("🔄 Conversation context reset! How can I help you?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and get responses from Claude."""
    user_message = update.message.text
    user_id = update.effective_user.id

    try:
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

    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
