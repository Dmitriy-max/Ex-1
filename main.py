#  ---------------------------------------------------------------------------
# Установим Selenium для Python
#  Для этого в теринале выполним команду: pip install selenium
#  ---------------------------------------------------------------------------

# импортируем необходимые библиотеки
# ----------------------------------------------------------------------------
import sys                          # для возможности получения парамтров
import os                           # для раболты с файлами, операционной системой
import json                         # для работы с json
import time                         # для возможности установки задержки выполнения команд

from selenium import webdriver      # Импортируем webdriver из библиотеки Selenium

#from selenium.webdriver.common.action_chains import ActionChains    # Импортируем ActionChains для выполнения цепочки действий
# ----------------------------------------------------------------------------


# проверим передались ли параметры
if len(sys.argv)<=1:
    os.system('cls' if os.name == 'nt' else 'clear')        # почистим экран терминала (с учетом ОС)
    print ("Параметры телефона не переданы.")
    print ("Пожалуйста, запустите скрипт с параметрами искомого телефона")
    exit()

# Определеим переменные
# ----------------------------------------------------------------------------
url = 'https://www.onliner.by' # Для url онлайнера

phone_model = ""
for arg in sys.argv[1:]:
    phone_model = phone_model + " " + arg

# параметры, которые хотим вывести в json файл
export_parametrs = {
    'Версия ОС на момент выхода'    : 'os_at_release',
    'Размер экрана'                 : 'screen_size',
    'Разрешение экрана'             : 'screen_res',
    'Оперативная память'            : 'ram',
    'Встроенная память'             : 'internal_mem',
    'Платформа'                     : 'platform',
    'Процессор'                     : 'processor',
    'Микроархитектура ЦПУ'          : 'cpu_arch'
    }

# итоговый список для экспорта в json
export_list = []
# ----------------------------------------------------------------------------

# Инициализация соответствующего веб-дайвера Chrome в Python

chrome_options = webdriver.ChromeOptions()                  # Переменная опций для запуска Хрома
chrome_options.add_argument('--headless')                   # опция запуска в фоновом режиме
chrome_options.add_argument('--ignore-certificate-errors')  # опция игнорирования ошибок серификатов
chrome_options.add_argument('--window-size=1500,900')       # опция размеров окна
chrome_options.page_load_strategy = "normal"                # дожидается загрузки всех ресурсов

driver = webdriver.Chrome(options=chrome_options)           # запуск Хрома с опциями

try:
    # Запустим браузер с начальной страницы онлайнера
    try:
        driver.get(url)
    except TimeoutError:
        print("Ошибка запуска браузера.\nПожалуйста, перезапустите скрипт")
        exit()

    # перейдем в "Кталог"
    driver.find_element('xpath','(// a [@href="https://catalog.onliner.by" and @class="b-main-navigation__link"])').click()               #через xpath

     # перейдем в "Смартфоны" через "Популярные категории"
    driver.find_element('xpath','(// a [@href="https://catalog.onliner.by/mobile"])').click()  #в

    driver.refresh()

    # поищем в быстром поиске
    fast_search = driver.find_element('xpath', '(//input[@class="fast-search__input"])')
    fast_search.clear()                                     # почистим фильтр быстрого поиска
    fast_search.send_keys(phone_model)

    time.sleep(3)

    # посчитаем количество совпадений по найденной модели
    count_model_found = driver.find_elements('xpath','(//div[@class="product__details"])')

    if len(count_model_found) > 1:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Найдено более одной модели, соответствующих заданным  поиска.")
        print("Пожалуйста, уточните критерии поиска и пперезапустите крипт с новыми параметрами")
        driver.quit()
        exit()
    if len(count_model_found) == 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Ммодели, соответствующих заданным  поиска, не найдено.")
        print("Пожалуйста, уточните критерии поиска и пперезапустите крипт с новыми параметрами")
        driver.quit()
        exit()

    # Перешли по ссылке найденного телефона
    driver.find_element('xpath', '(//div[@class="product__details"])').click()

    # Характеристики найденного телефона

    # таблица характеистик
    specs_table = driver.find_element('xpath', '(//table[@class="product-specs__table"])')

    # найдем разделы таблицы (specs_table_title)
    section_table = specs_table.find_elements('xpath', '(//table//tbody)')

    for section in section_table:
        title = section.find_element('class name','product-specs__table-title-inner').text.strip()
        rows = section.find_elements('tag name','tr')

        for row in rows[1:]:                # начать  1-й строки, т.е. пропустить строку заголовка
            columns = row.find_elements('tag name','td')
            col_0 = columns[0].text.strip()
            try:
                col_1 = columns[1].text.strip()
            except:
                col_1 = ''

            # проверим требуется ли выводить данный параметр в файл json
            if col_0 in export_parametrs:
                #print("\t", export_parametrs[col_0],"\t:",col_1)

                # создам список для вывода в файл json
                #export_list.append({col_0:col_1})                  # если ключ требуется выводить на русском (как на сайте)
                export_list.append({export_parametrs[col_0]:col_1}) # если ключ требуется выводить на анлийском

    # вывод json файла
    # проверим наличие папки, чтобы не сосзавать повторно
    if not os.path.isdir("export_folder"):
        os.mkdir("export_folder")

    with open(os.getcwd() + "\\export_file.json", "w") as file:
        json.dump(export_list, file, indent=4, ensure_ascii=False)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Результат работы в файле: ", os.getcwd() + "\\export_file.json")
# В случае ошибок, чтобы браузер обязательно закрылся
finally:
    driver.quit()

