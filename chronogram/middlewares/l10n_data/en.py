EN: dict[str, str] = {
    "no_state_error": "<b>Error when creating a time capsule.</b>\n"
    "Try restarting the capsule creation process /timecapsule\n"
    "(also delete the menu that caused this error to prevent it from happening again)",
    "cant_delete_msg": "Error on closing this menu. Delete manually",
    "inbox_altered": "Error. Restart /inbox",
    "tc_doesnt_exist": "This capsule doesn't exist. Restart /inbox",
    "default_response": "Unknown command/message\n\n"
    "To create a timecapsule, use /timecapsule first\n\n"
    "For additional help, use /help",
    "invoice_already_paid": "Already Paid",
    "/start": "Welcome to <b>Chronogram</b>,\n"
    "A personal time capsule bot designed to help you reflect on your past and rediscover yourself "
    "in the future.\n\n"
    "<b>With this bot, you will be able to send messages to your future self</b>\n\n"
    "Please ensure that everything is configured properly:\n"
    "- Your language: {}\n"
    "- Your local time: {}\n"
    "To change any of the above, use /settings\n\n"
    "If everything is in order, get started by typing /timecapsule and following the prompts to "
    "create your first time capsule\n\n"
    "Other commands:\n"
    "• /help - Help with usage\n"
    "• /about - About this bot (philosophy, goal, approach)\n"
    "• /inbox - This is where your received time capsules will be stored\n\n",
    "/help": "<b>Available commands</b>\n\n"
    "• /timecapsule - Start time capsule creation process\n"
    "• /settings - Your stats, language, timezone, storage, subscription\n"
    "• /about - About this bot (philosophy, goal, approach)\n"
    "• /inbox - Your received time capsules\n"
    "• /paysupport - Information about payments\n"
    "• /donate - Donate any amount of ⭐️ to the creator of this bot\n\n"
    "• /delete_everything - <b>NOT RECOMMENDED!</b> Delete all of your time capsules, including "
    "those yet to arrive.",
    "/about": "<b>Chronogram</b> is a personal time capsule bot designed for deep "
    "self-reflection. By sending messages to yourself in the future, "
    "you'll be able to revisit your past experiences, emotions, thoughts, "
    "and gain new insights into your personal growth.\n\n"
    "• Our objective is to elicit emotions and challenge your perspectives. "
    "We believe that by confronting your past self in such a personal setting, "
    "you will be able to develop a deeper understanding "
    "of yourself and the world around you.\n\n"
    "• Our approach is designed to ensure that that the version of you that sent the time capsule"
    " remains in control, "
    "without any <b>possibility of interference*</b> or manipulation by your future self. "
    "Once sent, your time capsule is sealed, "
    "remaining unchanged until the specified destination date and time. "
    "This ensures that your original intentions and thoughts remain intact, "
    "unknown to you until the capsule arrives. "
    "The destination date and content will be kept in secret from you, "
    "to add an element of surprise to your future self\n\n"
    "<i>*However, in order to comply with the privacy policy of Telegram, "
    "we must provide you with the ability to delete all your stored data at any time, "
    "including time capsules that have yet to arrive. (/delete_everything)</i>",
    "/paysupport": "<b>Payment Info</b>\n\n"
    "All payments in this bot are done using Telegram Stars⭐️\n\n"
    "<b>All payments to this bot are non-refundable</b>\n\n"
    "<i>If you have any questions regarding payments - @chronogram_support</i>",
    "/donate": {
        "usage": "<b>Usage:</b>\n\n"
        "<code>/donate *amount*</code>\n\n"
        "<b>All payments to this bot are non-refundable</b>",
        "confirm_title": "Confirm Donation",
        "confirm_descr": "Confirm your donation of {}⭐️\n\n",
        "success": "Thank you for your support\n\n<b>May the time be your ally</b>",
    },
    "/refund": {
        "no_refunds": "Refunds are not available with this bot",
        "usage": "<b>Refund usage</b>\n\n" "<code>/refund *ID of transaction*</code>",
        "invalid_tid": "Invalid transaction ID",
        "non_refund": "subscriptions are non refundable",
        "24passed": "This payment was made more than 24 hour ago",
        "already_refunded": "This payment is already refunded",
        "success": "Done",
    },
    "/timecapsule": {
        "init": "<b>Let's create a time capsule</b>\n\n"
        "Here are some rules:\n"
        "• It must be in text or/and an <b>image*</b> format\n"
        "• Text-only capsule must not exceed <b>1600</b> characters in length\n"
        "• If you attach an image, the caption must not exceed <b>800</b> characters in length\n"
        "• Do not submit any valuable or sensitive information\n\n"
        "<b>Important!</b>\nYou will lose access to the contents of "
        "your time capsule once it's sent, "
        "and only gain access to it after you've received it\n\n"
        "<i><b>*</b>Make sure to send your image as Photo, "
        'not as File (Checked "Compress the image")</i>'
        "\n\n<b>In your next message, enter content for your time capsule »</b>",
        "invalid_data": "Invalid data. Only text and/or image are supported\n\n"
        "If you submit an image, make sure to check "
        '"Compress the image" when you send it',
        "invalid_length": "You message exceeds allowed length of 1600 (your message length is {})",
        "invalid_caption_length": "Allowed length capsules with image is 800 (your message length is {})"
        "(your caption length is {})",
        "prompt_date": "<b>Select date of delivery (Only future dates are supported)</b>",
        "not_enough_space": {
            "common": "You dont have enough space to send this time capsule",
            "has_received": "\n\nYou can free some space by "
            "deleting some old time capsules "
            "from your /inbox",
            "not_sub": "\n\nYour current storage limit is 0.1MB.\n"
            "You can increase it to 10MB by <b>subscribing</b>\n"
            "(go to /settings -> Buy Subscription",
        },
        "only_future": "Only future dates are supported",
        "you_selected": "You selected ",
        "input_time": "You selected <b>{}</b>\n<b>Now select time of delivery</b>",
        "time_error": "Invalid time, try again",
        "confirm_no_text": "Your time capsule will be delivered on:\n<b>{}</b>",
        "canceled_no_text": "Time capsule canceled",
        "sent": "Time capsule sent, {} storage left",
        "received": "You have a message from You\nSent at: <b>{}</b>\n\n"
        "<tg-spoiler><blockquote>{}</blockquote></tg-spoiler>",
        "saved": "Saved in your /inbox, {} storage remaining",
        "delete": "\n\nAre you sure you want to <b>permanently delete</b> "
        "this time capsule?\nThis action cannot be undone",
        "deleted": "Time capsule erased, {} storage remaining",
    },
    "/inbox": {
        "init": "<b>Here are your saved time capsules.\n\n {} ({}) space left</b>",
        "subscribe": "\n\nTo increase storage space to <b>10MB(100 times more space)</b>, "
        "go to /settings -> Buy Subscription",
        "empty": "You dont have any received time capsules",
        "some_underway": "\n<b>(Some are underway)</b>",
        "timecapsule_data": "Sent: {}\nReceived: {}\n\n<blockquote>{}</blockquote>",
        "menu_col_sent": "sent:",
        "menu_col_received": "received:",
    },
    "/settings": {
        "init": "<b>Settings</b>\n\n"
        "Language:  {}\n\n"
        "Local time:  <b>{}</b>\n\n"
        "Storage left:  {}  (<b>{}</b>)\n\n",
        "donate": "<i>Thank the author of the bot by donating any amount of ⭐️:</i>\n"
        "<code>/donate *amount*</code>",
        "subscription_agitate": "<b>You can increase your storage space from 0.1MB to 10MB"
        " by paying for our monthly subscription (150⭐️)</b>\n\n",
        "subscription_expires": "Your subscription expires at <b>{}</b>\n\n",
        "language": "Switch language",
        "timezone": "Switch timezone",
        "subscription_buy": "Buy Subscription",
        "subscription_prolong": "Prolong Subscription",
        "close": "Close",
        "utc_picker_display_value": "Time according to selected: {}",
        "language_change_success": "Language changed.",
    },
    "buttons": {
        "cancel": "Cancel",
        "close": "Close",
        "got_it": "Got it",
        "keep": "Keep",
        "delete": "Delete",
        "back": "« Back",
        "confirm_delete": "Confirm Delete",
        "confirm": "Confirm",
        "send": "Send",
        "pay": "Pay {}⭐️",
        "buy_prolong": "Buy\\Prolong",
    },
    "/subscription": {
        "init_subscribed": "<b>Subscriptions</b>"
        "\n\nYour subscription expires at  <b>{}</b>\n\n",
        "init_standard": "<b>Subscriptions</b>\n\n",
        "info": "You can subscribe to ChronoPremium for 150⭐️(a month) to get 10MB available "
        "storage for your time "
        "capsules instead of standard 0.1MB. Please note that it's a monthly subscription "
        "and not paying for the next month in time will result in termination of used space above "
        "standard 0.1MB. You will be reminded of expiration of your subscription 1 day prior."
        "Subscription payments are <b>non refundable</b>\n\n"
        "You may prolong your subscription at any time."
        "use /paysupport for additional information regarding payments",
        "confirm_purchase": "Confirm Subscription Purchase",
        "confirm_subscription": "Confirm purchase of ChronoPremium "
        "for {} {} for {}⭐️.\n"
        "After payment, your subscription will last until:\n{}",
        "months": {1: "month", 3: "months", 6: "months", 12: "months", 120: "months"},
        "subscribe_1_month": "1 Month (150⭐️)",
        "subscribe_3_month": "3 Months (450⭐️)",
        "subscribe_6_month": "6 Months (900⭐️)",
        "subscribe_12_month": "12 Months (1800⭐️)",
        "subscribe_120_month": "120 Months (18000⭐️)",
        "subscription_deadline": "You subscription ends in 24 hours",
        "subscription_deadline_surplus": "You subscription ends in 24 hours, "
        "some amount of your time capsules may be erased"
        " (including those yet to arrive)",
        "subscription_deadline_prolong": "\n\n<b>Prolong your subscription:\n"
        "/settings » "
        '"Prolong Subscription"</b>',
        "subscription_activated": "Subscription granted. Active until {}",
        "subscription_prolonged": "Subscription prolonged. Active until {}",
    },
    "/delete_everything": {
        "init": "<b>Delete Everything</b>\n\n"
        "Are you sure you want to delete <b>ALL</b> your time capsules?\n"
        "There may be time capsule that have yet to arrive\n\n"
        "<b>THIS ACTION CANNOT BE UNDONE!\n"
        "We strongly advise against doing this</b>\n\n"
        "If you understand and wish to delete everything anyway, "
        'type:\n"Yes, I want to permanently delete all my time capsules"',
        "confirmation_message": "Yes, I want to permanently delete all my time capsules",
        "confirmation_message_invalid": "Invalid confirmation. Canceling deletion",
        "success": "<b>Everything deleted</b>",
    },
}
