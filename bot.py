import logging
import requests
from random import choice
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Predefined Dork Templates
DORK_TEMPLATES = {
    "site_search": "site:{}",
    "filetype": "filetype:{} {}",
    "index_of": "intitle:'index of' {}",
    "login_pages": "inurl:login {}",
    "admin_pages": "inurl:admin {}",
    "emails": "intext:'@{}' {}",
    "sensitive_files": "filetype:sql | filetype:txt | filetype:log {}",
}

# List of User-Agent strings for web requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Welcome to Over Dorker!\n\n"
        "I can help you perform advanced web searches using predefined templates or custom queries.\n"
        "Use /help or /use to learn how to use this bot effectively!"
    )

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 **How to Use**:\n\n"
        "1️⃣ **Custom Query**:\n"
        "Use `/dork <query>` to perform a custom search.\n"
        "Example: `/dork site:example.com`\n\n"
        "2️⃣ **Use Templates**:\n"
        "Use `/dork template:<name> <args>` for predefined searches.\n"
        "Example: `/dork template:site_search example.com`\n\n"
        "3️⃣ **View Templates**:\n"
        "Use `/templates` to see all available templates.\n\n"
        "🔗 **Note**: The bot provides clickable search links for Google and DuckDuckGo."
    )

# Dorking Guide Command
async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🛠 **Dorking Guide**:\n\n"
        "Dorking is a technique used to uncover hidden information by crafting advanced search queries. Here's how to use it effectively:\n\n"
        "1️⃣ **What is Dorking?**\n"
        "It involves using search engines like Google to find sensitive information such as exposed files, login pages, or admin panels.\n\n"
        "2️⃣ **Key Search Operators**:\n"
        "- `site:<domain>`: Restrict results to a specific site.\n"
        "- `filetype:<extension>`: Search for specific file types (e.g., PDF, SQL).\n"
        "- `intitle:<text>`: Find pages with specific words in their title.\n"
        "- `inurl:<text>`: Search for specific words in URLs.\n\n"
        "3️⃣ **Examples**:\n"
        "- Search for exposed PDFs: `filetype:pdf site:example.com`\n"
        "- Find admin login pages: `inurl:admin site:example.com`\n"
        "- Locate database files: `filetype:sql intitle:'index of'`\n\n"
        "4️⃣ **Tips**:\n"
        "- Use `/templates` to see predefined dorks for common scenarios.\n"
        "- Be responsible and ensure you have permission to perform searches for sensitive data."
    )

# List Predefined Templates
async def templates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    templates_message = "\n".join([f"- `{name}`: {template}" for name, template in DORK_TEMPLATES.items()])
    await update.message.reply_text(
        f"📋 **Predefined Templates**:\n\n{templates_message}\n\n"
        "👉 Use `/dork template:<name> <args>` to apply a template."
    )

# Perform Search
async def dork(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("❗ Please provide a search query. Use /help for instructions.")
        return

    # Check if the query uses a template
    query = " ".join(context.args)
    if query.startswith("template:"):
        parts = query.split(" ")
        template_name = parts[0][9:]
        args = parts[1:]
        if template_name not in DORK_TEMPLATES:
            await update.message.reply_text(f"❌ Template `{template_name}` not found. Use /templates to see available templates.")
            return
        try:
            query = DORK_TEMPLATES[template_name].format(*args)
        except IndexError:
            await update.message.reply_text("❌ Incorrect arguments for the template. Use /templates to check usage.")
            return

    await update.message.reply_text(f"🔍 Performing search for: `{query}`")

    # Perform Google and DuckDuckGo searches
    google_url = f"https://www.google.com/search?q={query}"
    duckduckgo_url = f"https://duckduckgo.com/?q={query}"

    headers = {"User-Agent": choice(USER_AGENTS)}  # Randomize User-Agent

    # Fetch Google results (only returns links to search engine)
    try:
        google_response = requests.get(google_url, headers=headers)
        if google_response.status_code == 200:
            google_result = f"🔗 [Google Results](<{google_url}>)"
        else:
            google_result = "❌ Google search failed."
    except Exception as e:
        google_result = f"❌ Error with Google search: {e}"

    # Fetch DuckDuckGo results
    try:
        duckduckgo_response = requests.get(duckduckgo_url, headers=headers)
        if duckduckgo_response.status_code == 200:
            duckduckgo_result = f"🔗 [DuckDuckGo Results](<{duckduckgo_url}>)"
        else:
            duckduckgo_result = "❌ DuckDuckGo search failed."
    except Exception as e:
        duckduckgo_result = f"❌ Error with DuckDuckGo search: {e}"

    # Send results back to the user
    await update.message.reply_text(
        f"🔎 **Search Results**:\n\n{google_result}\n{duckduckgo_result}",
        parse_mode="Markdown",
    )

# Main Function
def main():
    # Updated Bot Token
    application = ApplicationBuilder().token("7411902169:AAFbfcS2UMW0C9wt_lNzdGYz6xql1pqPwzA").build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("use", use_command))
    application.add_handler(CommandHandler("templates", templates))
    application.add_handler(CommandHandler("dork", dork))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
