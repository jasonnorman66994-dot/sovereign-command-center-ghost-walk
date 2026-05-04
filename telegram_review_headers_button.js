// Node.js snippet to add 'Review Headers' button to the Telegram alert (Telegraf)

const { Markup } = require('telegraf');

// ...inside your alert sending logic:
const alertId = data.id; // Use a unique ID for the alert (e.g., filename or DB id)

const buttons = [
  [
    Markup.button.callback('🔍 Review Headers', `headers_${alertId}`)
    // ...add other buttons as needed
  ]
];

const extra = {
  parse_mode: 'MarkdownV2',
  reply_markup: Markup.inlineKeyboard(buttons)
};

// When sending the alert:
// await ctx.replyWithMarkdownV2(alertMessage, extra);
// or
// bot.telegram.sendMessage(chatId, alertMessage, extra);

// Handler for the button (see previous examples for full handler):
bot.on('callback_query', async (ctx) => {
  const [action, id] = ctx.callbackQuery.data.split('_');
  if (action === 'headers') {
    // Fetch and display headers for this alert
    // ...see previous handler example
  }
});
