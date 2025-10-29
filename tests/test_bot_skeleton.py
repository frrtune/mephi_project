!pip install pytelegrambotapi

import telebot
from google.colab import userdata
import json
TEST_BOT_TOKEN = userdata.get('TEST_BOT_TOKEN')
bot = telebot.TeleBot(TEST_BOT_TOKEN)
test_history = []

def run_test_suite():
    """Функция для запуска тестовых сценариев"""
    print("=== ТЕСТОВЫЕ СЦЕНАРИИ ===")
    test_scenarios = [
        "",
        "Привет",
        "Hello", 
        "123",
        "@#$%",
        "😊",
        "A",
        "' OR '1'='1",
        "<script>alert('test')</script>"
    ]
    print("Подготовьтесь к ручному тестированию следующих сценариев:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"{i}. '{scenario}'")
    return test_scenarios
@bot.message_handler(commands=['start'])
def send_welcome(message):
    test_history.append({
        "type": "command", 
        "command": "start", 
        "user_id": message.from_user.id,
        "timestamp": message.date
    })
    bot.reply_to(message, "Привет! Это тестовый бот для проверки каркаса. Отправь мне любое сообщение.")
@bot.message_handler(commands=['help'])
def send_help(message):
    test_history.append({
        "type": "command", 
        "command": "help", 
        "user_id": message.from_user.id,
        "timestamp": message.date
    })
    help_text = """
Доступные команды:
/start - начать работу  
/help - показать справку

Просто отправьте сообщение для тестирования.
    """
    bot.reply_to(message, help_text)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_message = message.text
    test_case = {
        "type": "message",
        "content": user_message,
        "length": len(user_message),
        "user_id": message.from_user.id,
        "timestamp": message.date
    }
    test_history.append(test_case)
    response = f"Тест пройден! Вы написали: '{user_message}'\nДлина: {len(user_message)} символов"
    bot.reply_to(message, response)
run_test_suite()
print("\n=== БОТ ЗАПУЩЕН ===")
print("Протестируйте бота, отправляя сообщения из списка выше")
print("Для просмотра истории тестов выполните: print(test_history)")
print("Бот запускается...")
try:
    bot.polling(none_stop=True, timeout=60)
except Exception as e:
    print(f"Ошибка при запуске бота: {e}")


def analyze_test_results():
    """Анализ результатов тестирования"""
    print("=== АНАЛИЗ РЕЗУЛЬТАТОВ ТЕСТИРОВАНИЯ ===")   
    if not test_history:
        print("❌ Тестирование еще не проводилось!")
        return 
    commands = [t for t in test_history if t['type'] == 'command']
    messages = [t for t in test_history if t['type'] == 'message']
    print(f"📊 Всего операций: {len(test_history)}")
    print(f"🔄 Команд: {len(commands)}")
    print(f"💬 Сообщений: {len(messages)}")   
    print("\n✅ ПРОВЕРЕННЫЕ КОМАНДЫ:")
    for cmd in commands:
        print(f"  - /{cmd['command']}")    
    print("\n✅ ПРОВЕРЕННЫЕ СООБЩЕНИЯ:")
    for msg in messages[:10]:  
        content = msg['content']
        print(f"  - '{content}' ({len(content)} символов)")
    if len(messages) > 10:
        print(f"  ... и еще {len(messages) - 10} сообщений")
analyze_test_results()


print("=== РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ===")
print(f"Всего записей в истории: {len(test_history)}")
for i, item in enumerate(test_history):
    if item['type'] == 'command':
        print(f"{i+1}. Команда: /{item['command']}")
    else:
        print(f"{i+1}. Сообщение: '{item['content']}'")
