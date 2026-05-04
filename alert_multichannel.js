const nodemailer = require('nodemailer');
const { WebClient } = require('@slack/web-api');
const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config();

const telegramBot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN);
const slack = new WebClient(process.env.SLACK_BOT_TOKEN);
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
});

async function sendAlertMultiChannel(alert) {
    // Telegram
    await telegramBot.sendMessage(process.env.TELEGRAM_CHAT_ID, alert.message, { parse_mode: 'Markdown' });
    // Slack
    await slack.chat.postMessage({ channel: process.env.SLACK_CHANNEL, text: alert.message });
    // Email
    await transporter.sendMail({
        from: process.env.EMAIL_USER,
        to: process.env.ALERT_EMAIL,
        subject: 'Security Alert',
        text: alert.message
    });
    // Webhook (optional)
    if (process.env.WEBHOOK_URL) {
        await fetch(process.env.WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(alert)
        });
    }
}

module.exports = { sendAlertMultiChannel };
