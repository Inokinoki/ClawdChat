# ClawdChat - Telegram Bot with Claude AI

A simple, fast Telegram bot powered by Claude AI using the Anthropic API SDK.

## Features

- 🤖 **AI-Powered**: Uses Claude AI for intelligent responses
- 💾 **Conversation Memory**: Remembers context within conversations
- 🌐 **Custom API Support**: Works with any Anthropic-compatible API
- 📝 **Natural Conversations**: Friendly, helpful interactions
- 🔧 **Easy Setup**: Simple configuration with environment variables
- ⚡ **Fast**: Uses `uv` package manager for lightning-fast dependency management

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (fast Python package manager) OR pip
- Anthropic-compatible API key
- Telegram Bot token ([Get one from @BotFather](https://t.me/botfather))

## Quick Start

### 1. Install Dependencies

```bash
# Install uv if you haven't already (one-time setup)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv (super fast!)
uv sync
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your API credentials
nano .env  # or use your preferred editor
```

Add your credentials to `.env`:
```env
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com  # Optional: custom endpoint
ANTHROPIC_MODEL=claude-opus-4-6                 # Optional: custom model

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

### 3. Test Configuration

```bash
# Test your API connection
uv run python test_new_config.py
```

### 4. Run the Bot

```bash
# Make sure no old environment variables are set
unset ANTHROPIC_BASE_URL ANTHROPIC_API_KEY

# Start the bot
uv run python telegram_bot_simple.py
```

### 5. Use Your Bot

1. Open Telegram
2. Search for your bot by username (from @BotFather)
3. Click "Start" or send `/start`
4. Start chatting!

## Using Make Commands (Optional)

If you have `make` installed, you can use these shortcuts:

```bash
make help          # Show all available commands
make install       # Install dependencies
make test          # Test configuration
make run-advanced  # Run the bot
make clean         # Clean cache files
```

## Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Display help information
- `/reset` - Clear conversation memory

## Customization

### Files

- `telegram_bot_simple.py` - Main bot implementation (edit this to customize behavior)
- `test_new_config.py` - API connection tester

### Configurable Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `ANTHROPIC_BASE_URL` | Custom API endpoint | `https://api.anthropic.com` |
| `ANTHROPIC_MODEL` | Model to use | `claude-opus-4-6` |
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather | Required |

### Custom Models & Endpoints

The bot works with any Anthropic-compatible API. For example:

**DashScope (Alibaba Cloud):**
```env
ANTHROPIC_API_KEY=your_dashscope_key
ANTHROPIC_BASE_URL=https://coding.dashscope.aliyuncs.com/apps/anthropic
ANTHROPIC_MODEL=qwen3.5-plus
```

**Other compatible APIs:**
Just set `ANTHROPIC_BASE_URL` and `ANTHROPIC_MODEL` accordingly.

## Project Structure

```
ClawdChat/
├── telegram_bot_simple.py  # Main bot implementation
├── test_new_config.py      # API connection test
├── pyproject.toml          # Dependencies (uv)
├── Makefile                # Convenient commands
├── .env.example            # Environment template
├── README.md               # This file
├── QUICKSTART.md           # Quick start guide
├── UV_GUIDE.md             # uv package manager guide
└── UV_REFERENCE.md         # Quick uv reference
```

## Deployment

### Running in Background

```bash
# Start in background
uv run python telegram_bot_simple.py > /dev/null 2>&1 &

# Check if running
ps aux | grep "telegram_bot_simple" | grep -v grep

# Stop the bot
pkill -f "telegram_bot_simple.py"
```

### Using systemd (Linux)

Create `/etc/systemd/system/clawdchat.service`:
```ini
[Unit]
Description=ClawdChat Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/ClawdChat
ExecStart=/usr/bin/uv run python telegram_bot_simple.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable clawdchat
sudo systemctl start clawdchat
```

## Troubleshooting

### Bot doesn't respond
- Check if the bot is running: `ps aux | grep telegram_bot_simple`
- Verify your `.env` file has correct API keys
- Check bot logs for errors

### API authentication errors
- Verify your API key is valid
- Check if the API endpoint is correct
- Some providers require specific model names

### Model errors
- The bot automatically handles different content block types
- If you see `ThinkingBlock` errors, the code handles this automatically
- Make sure `ANTHROPIC_MODEL` is supported by your API provider

### Python version issues
```bash
# Check your version
python --version

# Install correct version if needed
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11
```

## Security Best Practices

1. **Never commit `.env` to version control**
2. **Use environment variables for sensitive data**
3. **Rotate API keys periodically**
4. **Monitor API usage**
5. **Keep dependencies updated**

## Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [UV_GUIDE.md](UV_GUIDE.md) - Comprehensive uv guide
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## License

MIT License - feel free to use and modify!

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
