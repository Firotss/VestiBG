from bs4 import BeautifulSoup #обработване на html файл
import requests #свързване към сайт
import telebot #връзка с бот
import sqlite3 #връзка с база данни

bot = telebot.TeleBot('1496797291:AAFUCF3PBwNEJMj82XMNZMA7Kw0SET4vIF0') #токен бота 

# 1. Намерете бот в телеграм- @VestiBG_bot
# 2. Стартирайте тоя код
# 3. Можете да ползвате бот!
# p.s можете да променете токен на свой


cn = sqlite3.connect('database.db')#свързване с база данни
cur = cn.cursor()#създаване на курсор на база данни 
cur.execute("CREATE TABLE IF NOT EXISTS savenews(id TEXT, link TEXT, title TEXT)")#създаване на таблица в база данни в случаи на нейното отсътствие

def req(url): #метод за получаване на код на страница
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup

def delete(message, i):
    bot.delete_message(message.chat.id, message.message_id - i)

#създаване на специални клавиатури
menu_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
news_keyboard= telebot.types.ReplyKeyboardMarkup(True, True, True) 
newsMenu_keyboard = telebot.types.ReplyKeyboardMarkup(True, True, True, True)
saves_keyboard = telebot.types.ReplyKeyboardMarkup(True, True, True)
menu_keyboard.row('новини','запазени статии')
news_keyboard.row('следваща','запазване','назад') 
newsMenu_keyboard.row('последни новини','търсене по дума','назад')
saves_keyboard.row('следваща','изтриване','назад')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Изберете бутон:" ,reply_markup=menu_keyboard)

@bot.message_handler(content_types=['text'])
def start_code(message):
    choice = message.text
    if choice == 'новини': 
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        bot.send_message(message.chat.id,"Изберете бутон:",reply_markup=newsMenu_keyboard)
        bot.register_next_step_handler(message, news_menu);
    elif choice == 'запазени статии':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        i = 1
        load(message,i)
    else:
        bot.register_next_step_handler(message, start_code);


#новини
def news_menu(message):
    choice = message.text
    if choice == 'последни новини':
        delete(message, 0)
        delete(message, 1)
        i = 0
        url = "https://www.vesti.bg/posledni-novini"
        give_news(message,i,url)
    elif choice == 'търсене по дума':
        delete(message, 0)
        delete(message, 1)
        bot.send_message(message.chat.id,"Въведете дума")
        bot.register_next_step_handler(message, prehod);
    elif choice == 'назад':
        delete(message, 0)
        delete(message, 1)
        bot.send_message(message.chat.id,"Вие се върнахте обратно")
        start_message(message)
    else:
        bot.register_next_step_handler(message, news_menu);

#запазени статии
def load(message, i):
        cn = sqlite3.connect('database.db')
        cur = cn.cursor()
        c = [message.chat.id]
        n = 1
        for y in (cur.execute("SELECT * FROM savenews WHERE id = ?",c)):
            if n < i:
                n+=1
            elif n == i:
                bot.send_message(message.chat.id,"Новина:",reply_markup=saves_keyboard)
                button = telebot.types.InlineKeyboardMarkup()
                url_button = telebot.types.InlineKeyboardButton(text="Към статията", url=y[1])
                button.add(url_button)
                bot.send_message(message.chat.id, y[2], reply_markup=button)
                bot.register_next_step_handler(message, save_menu,i);
                break
        else:
            bot.send_message(message.chat.id,"Статия не намерена")
            start_message(message)
#меню на запазени статии
def save_menu(message,i):
    choice = message.text
    if choice == 'следваща':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        i+=1
        load(message,i)
    elif choice == 'изтриване':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        delete_save(message,i)
    elif choice == 'назад':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        bot.send_message(message.chat.id,"Вие се върнахте обратно")
        start_message(message)
    else:
        bot.register_next_step_handler(message, save_menu, i);
#меню за изтриване на запазени статии
def delete_save(message,i):
        cn = sqlite3.connect('database.db')
        cur = cn.cursor()
        c = [message.chat.id]
        n = 1
        for y in (cur.execute("SELECT * FROM savenews WHERE id = ?",c)):
            if n < i:
                n+=1
            elif n == i:
                d = [c[0],y[1]]
                cur.execute("DELETE FROM savenews WHERE id = ? AND link = ?",d)
                cn.commit()
                cn.close()
                bot.send_message(message.chat.id,"Статия е изтрита",reply_markup=saves_keyboard)
                load(message,i)
                break

#последни новини/търсене по дума
def prehod(message):
    name = message.text
    url = "https://www.vesti.bg/tarsene?q="+name+"&t=on"
    i = 0
    give_news(message,i,url)

def give_news(message,i,url):
        soup = req(url)
        for y in soup.find_all('a', class_="gtm-ListNews-click")[i:]:
            bot.send_message(message.chat.id,"Новина:",reply_markup=news_keyboard)
            b = req(y.get("href"))
            button = telebot.types.InlineKeyboardMarkup()
            url_button = telebot.types.InlineKeyboardButton(text="Към статията", url=y.get("href"))
            button.add(url_button)
            bot.send_message(message.chat.id, b.title, reply_markup=button)
            bot.register_next_step_handler(message, searchnews,url,i);
            break
        else:
            bot.send_message(message.chat.id,"Статия не намерена",reply_markup=menu_keyboard)
            bot.register_next_step_handler(message, start_code);

#меню за преход между новини
def searchnews(message,url,i):
    choice = message.text
    if choice == 'следваща':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        i+=1
        give_news(message,i,url)
    elif choice == 'запазване':
        delete(message, 0)
        save(message,i,url)
    elif choice == 'назад':
        delete(message, 0)
        delete(message, 1)
        delete(message, 2)
        bot.send_message(message.chat.id,"Вие се върнахте обратно")
        start_message(message)
    else:
        bot.register_next_step_handler(message,searchnews,url,i)

#метод за съхранение
def save(message,i,url):
    soup = req(url)
    cn = sqlite3.connect('database.db')
    cur = cn.cursor()
    str = "статия е добавена"
    for y in soup.find_all('a', class_="gtm-ListNews-click")[i:]:
            b = req(y.get("href"))
            g = [message.chat.id]
            data = [message.chat.id,y.get("href"),b.title.text]
            for ii in cur.execute("SELECT * FROM savenews WHERE id = ?",g):
                if ii[1] == data[1]:
                    str = "такава статия вече е добавена"
                    break
            else: 
                cur.execute("INSERT INTO savenews VALUES(?, ?, ?)", data)
            cn.commit()
            cn.close()
            bot.send_message(message.chat.id, str,reply_markup=news_keyboard)
            delete(message, 1)
            delete(message, 2)
            give_news(message,i,url)
            break

bot.polling()