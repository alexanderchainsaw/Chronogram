RU: dict[str, str] = {
    "no_state_error": "<b>Ошибка при создании капсулы времени.</b>\n"
                      "Попробуйте перезапустить процесс создания капсулы /timecapsule\n"
                      "(а также удалите меню которое вызвало эту ошибку чтобы предотвратить  повторное "
                      "появление этой ошибки)",
    "cant_delete_msg": "Ошибка при закрытии меню. Удалите вручную",
    "inbox_altered": "Ошибка. Перезапустите /inbox",
    "tc_doesnt_exist": "Этой капсулы не существует. Перезапустите /inbox",
    "default_response": "Неизвестная команда/сообщение\n\n"
                        "Чтобы создать капсулу времени, введите /timecapsule\n\n"
                        "Для дополнительной информации, используйте /help",
    "invoice_already_paid": "Уже оплачено",
    "/start": "Добро пожаловать в <b>Chronogram</b>,\n"
              "Бот для создания личных капсул времени, который поможет вам порефлексировать над своим "
              "прошлым и заново открыть себя в будущем.\n\n"
              " <b>С помощью этого бота вы сможете отправлять сообщения будущим версиям себя</b>\n\n"
              "Пожалуйста, убедитесь, что все настроено правильно:\n"
              "- Ваш язык: {}\n"
              "- Ваше время: {}\n"
              "Чтобы изменить что-либо из вышеперечисленного, используйте /settings\n\n"
              "Если всё в порядке, используйте /timecapsule чтобы начать процесс создания "
              "вашей первой капсулы времени\n\n"
              "Другие команды:\n"
              "• /help - Помощь в использовании\n"
              "• /about - Об этом боте (философия, цель, подход)\n"
              "• /inbox - Тут будут храниться ваши полученные капсулы времени \n\n",
    "/help": "<b>Доступные команды</b>\n\n"
             "• /timecapsule - Начать процесс создания капсулы времени\n"
             "• /settings - Ваши данные, язык, часовой пояс, хранилище и подписка\n"
             "• /about - Об этом боте (философия, цель, подход)\n"
             "• /inbox - Ваши полученные капсулы времени\n"
             "• /paysupport - Информация о платежах\n"
             "• /donate - Подарить любое количество ⭐️ создателю этого бота\n\n"
             "• /delete_everything - <b>НЕ РЕКОМЕНДУЕТСЯ!</b> Удалить все ваши капсулы времени, "
             "включая те, что ещё не пришли",
    "/about": "<b>Chronogram</b> - бот для создания личных капсул времени, который служит "
              "инструментом для глубокой саморефлексии. Отправляя сообщения своей будущей версии себя, "
              "у вас появится возможность вернуться к своему прошлому опыту, эмоциям, мыслям, и "
              "получить новые знания о своем личном росте.\n\n"

              "• Наша цель - вызвать эмоции и бросить вызов вашим взглядам. "
              "Мы верим, что увидив себя из прошлого в такой личной обстановке, "
              "вы сможете достичь более глубокого понимания себя и окружающего мира\n\n"

              "• Наш подход - гарантировать, что именно та версия вас, которая отправила капсулу времени в прошлом,"
              "обладает наибольшей властью без какой-либо <b>возможности вмешательства*</b> "
              "или манипуляций со стороны вас в будущем. "
              "После отправки ваша капсула времени запечатывается "
              "и остается неизменной до указанной даты и времени назначения. "
              "Это гарантирует, что ваши первоначальные намерения и мысли останутся нетронутыми "
              "до того момента, пока капсула времени не прибудет. "
              "Дата назначения и содержание будут храниться в секрете от вас "
              "чтобы добавить элемент неожиданности для вас в будущем\n\n"

              "<i>*Однако в целях соблюдения политики конфиденциальности Telegram, "
              "мы обязаны предоставить вам возможность удалить все ваши сохраненные данные в любое время, "
              "включая капсулы времени, которые еще не прибыли. (/delete_everything)</i>",

    "/paysupport": '<b>Информация об оплате</b>\n\n'
                   'Все платежи в этом боте осуществляются с помощью Telegram Stars⭐️\n\n'
                   '<b>Все платежи этому боту не подлежат возврату.</b>\n\n'
                   '<i>Если у вас возникли вопросы касаемо оплат - @chronogram_support</i>',
    # 'Subscription payments are <b>non-refundable</b>\n'
    # 'Only <b>donations*</b> made less than 24 hours ago can be refunded\n'
    # 'To refund, use /refund\n\n'
    # '<i>*Payments made with /donate command</i>',
    "/donate": {"usage": "<b>Использование:</b>\n\n"
                         "<code>/donate *количество*</code>\n\n"
                         "<b>Все платежи этому боту не подлежат возврату.</b>",
                "confirm_title": "Подтверждение Оплаты",
                "confirm_descr": "Подтвердите отправку подарка {}⭐️\n\n",
                "success": "Спасибо за вашу поддержку\n\n<b>Пусть время будет вашим союзником</b>"},
    "/refund": {"no_refunds": "Все платежи этому боту не подлежат возврату.",
                "usage": "<b>Refund usage</b>\n\n"
                         "<code>/refund *ID of transaction*</code>",
                "invalid_tid": "Invalid transaction ID",
                "non_refund": "subscriptions are non refundable",
                "24passed": "This payment was made more than 24 hour ago",
                "already_refunded": "This payment is already refunded",
                "success": "Done"},
    "/timecapsule": {"init": "<b>Давайте создадим капсулу времени</b>\n\n"
                             "Несколько правил:\n"
                             "• Содержимое должно быть текстом и/или <b>изображением*</b>\n"
                             "• Исключительно-текстовые капсулы не должны превышать длину в <b>1600</b> символов\n"
                             "• Текст в капсулах с прикреплённым изображением не должен превышать длину"
                             " в <b>800</b> символов\n"
                             "• Не вводите ценную или конфиденциальную информацию\n\n"
                             "<b>Важно!</b>\nВы потеряете доступ к содержимому временной капсулы как только "
                             "она будет отправлена, "
                             "а вновь обретёте доступ только когда она придёт\n\n"
                     '<i><b>*</b>Убедитесь что отправляете ваше изображение как Фото а не как Файл '
                             '(Выбрано "Сжать изображение")</i>\n\n'
                             '<b>В вашем следующем сообщении, введите содержимое для вашей капсулы времени »</b>',
                     "invalid_data": 'Неподдерживаемый формат. Принимается только текст и/или изображение\n\n'
                                     'Если отправляете изображение, убедитесь что выбрано "Сжать изображение"',
                     "invalid_length": "Длина текста превышает допустимый лимит в 1600 символов (длина вашего "
                                       "текста - {})",
                     "invalid_caption_length": "Допустимая длина текста для капсул с изображением - 800"
                                               " (ваша длина {})",
                     "prompt_date": "<b>Выберите дату доставки (Поддерживаются только будущие даты)</b>",
                     "not_enough_space": {"common": "У вас недостаточно места для отправки этой капсулы",
                                          "has_received": "\n\nВы можете освободить пространство удалив старые"
                                                          " капсулы времени в вашем /inbox",
                                          "not_sub": "\n\nВаш текущий лимит хранилища составляет 0.1MB.\n"
                                                     "Вы можете увеличить его до 10MB"
                                                     " с помощью <b>подписки</b>\n"
                                                     "(отправляйтесь в /settings -> Купить Подписку"},
                     "only_future": 'Поддерживаются только будущие даты',
                     "you_selected": "Вы выбрали ",
                     "input_time": "Вы выбрали <b>{}</b>\n<b>Теперь выберите время</b>",
                     "time_error": "Неправильное время, попробуйте еще раз",
                     # "confirm": "Ваша капсула времени:\n\n<blockquote>{}</blockquote>\n\nбудет доставлена:\n<b>{}</b>",
                     "confirm_no_text": "Ваша капсула времени будет доставлена:\n<b>{}</b>",
                     # "canceled": "Создание капсулы времени отменено, сообщение: <blockquote>{}</blockquote>",
                     "canceled_no_text": "Создание капсулы времени отменено",
                     "sent": "Отправлено, места в хранилище: {}",
                     "received": "Получено сообщение от Вас\nОтправлено: <b>{}</b>\n\n"
                                 "<tg-spoiler><blockquote>{}</blockquote></tg-spoiler>",
                     "saved": "Сохранено в вашем /inbox, осталось {} места",
                     "delete": "\n\nВы уверены что хотите <b>безвозвратно удалить</b> "
                               "эту капсулу времени?\nЭто действие необратимо",
                     "deleted": "Капсула времени удалена, места в хранилище: {}"},
    "/inbox": {"init": "<b>Ваши сохранённые капсулы времени\n\nОсталось {} ({}) места</b>",
               "subscribe": "\n\nЧтобы увеличить место до <b>10MB (в 100 раз больше чем сейчас)</b>, "
                            "отправляйтесь в /settings -> Купить Подписку",
               "empty": "У вас нет полученых капсул времени",
               "some_underway": "\n<b>(Но есть неполученые)</b>",
               "timecapsule_data": "Отправлено: {}\nПолучено: {}\n<blockquote>{}</blockquote>",
               "menu_col_sent": 'отправлено:',
               "menu_col_received": 'получено:'},
    "/settings": {"init": "<b>Настройки</b>\n\n"
                          "Язык:  {}\n\n"
                          "Время:  <b>{}</b>\n\n"
                          "Места в хранилище:  {}  (<b>{}</b>)\n\n",
                  "donate": "<i>Поблагодарить автора бота любым количеством ⭐️:</i>\n"
                            "<code>/donate *количество*</code>",
                  "subscription_agitate": "<b>Вы можете увеличить место в хранилище с 0.1MB до 10MB"
                                          " с помощью ежемесячной подписки на нашего бота (150⭐️)</b>\n\n",
                  "subscription_expires": "Ваша подписка истечёт <b>{}</b>\n\n",
                  "language": "Сменить язык",
                  "timezone": "Сменить часовой пояс",
                  "subscription_buy": "Купить Подписку",
                  "subscription_prolong": "Продлить Подписку",
                  "close": "Закрыть",
                  "utc_picker_display_value": "Время согласно выбранному значению: {}",
                  "language_change_success": "Язык изменён."},
    "buttons": {"cancel": 'Отменить',
                "close": 'Закрыть',
                "got_it": 'Понятно',
                "keep": 'Оставить',
                "delete": 'Удалить',
                "back": "« Назад",
                "confirm_delete": "Подтвердить Удаление",
                "confirm": "Подтвердить",
                "send": "Отправить",
                "pay": "Заплатить {}⭐️",
                "buy_prolong": "Купить\\Продлить"},
    "/subscription": {"init_subscribed": "<b>Подписка</b>"
                                         "\n\nВаша подписка истечёт <b>{}</b>\n\n",
                      "init_standard": "<b>Подписка</b>\n\n",
                      "info":
                          "You can subscribe to ChronoPremium for 150⭐️(a month) to get 10MB available "
                          "storage for your time "
                          "capsules instead of standard 0.1MB. Please note that it's a monthly subscription "
                          "and not paying for the next month in time will result in termination of used space above "
                          "standard 0.1MB. You will be reminded of expiration of your subscription 1 day prior."
                          "Subscription payments are <b>non refundable</b>\n\n"
                          "You may prolong your subscription at any time."
                          "use /paysupport for additional information regarding payments",
                      "confirm_purchase": "Подтвердите оплату подписки",
                      "confirm_subscription": "Подтвердите покупку подписки ChronoPremium "
                                              "на {} {} за {}⭐️.\n"
                                              "После покупки, ваша подписка будет активна до:\n{}",
                      "months": {1: "месяц", 3: "месяца", 6: "месяцев", 12: "месяцев", 120: "месяцев"},
                      "subscribe_1_month": "1 Месяц (150⭐️)",
                      "subscribe_3_month": "3 Месяца (450⭐️)",
                      "subscribe_6_month": "6 Месяцев (900⭐️)",
                      "subscribe_12_month": "12 Месяцев (1800⭐️)",
                      "subscribe_120_month": "120 Месяцев (18000⭐️)",
                      "subscription_deadline": "Осталось меньше 24 часов до того как закончится ваша подписка",
                      "subscription_deadline_surplus": "Осталось меньше 24 часов до того как закончится ваша подписка, "
                                                       "некоторое количество ваших капсул времени может быть удалено"
                                                       " (В том числе и капсулы, которые находятся в пути)",
                      "subscription_deadline_prolong": '\n\n<b>Продлить подписку:\n'
                                                       '/settings » "Продлить Подписку"</b>',
                      "subscription_activated": "Подписка активирована. Закончится {}",
                      "subscription_prolonged": "Подписка продлена. Закончится {}",
                      },
    "/delete_everything": {'init': "<b>Удалить Всё</b>\n\n"
                                   "Вы уверены что хотите удалить <b>ВСЕ</b> ваши капсулы времени?\n"
                                   "Возможно что у вас есть капсулы времени которые еще не пришли\n\n"
                                   "<b>ЭТО ДЕЙСТВИЕ НЕОБРАТИМО!\n"
                                   "Мы настоятельно не рекомендуем этого делать</b>\n\n"
                                   "Если вы всё равно хотите всё удалить, напишите:"
                                   '\n"Да, Я хочу безвозвратно удалить все мои капсулы времени"',
                           "confirmation_message": "Да, Я хочу безвозвратно удалить все мои капсулы времени",
                           "confirmation_message_invalid": "Неверное подтверждение. Удаление отменено",
                           "success": "<b>Всё удалено</b>"}

}