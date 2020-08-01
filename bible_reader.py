import time
import telegram
import regex as re
from datetime import datetime
from config import TelegramTokens, ConfigBibleReader


class TelegramBibleReading(TelegramTokens, ConfigBibleReader):

    def __init__(self):
        TelegramTokens.__init__(self)
        ConfigBibleReader.__init__(self)
        self.now = datetime.now()
        self.month, self.day = self.now.month, self.now.day
        self.dow = self.__DAYS_OF_WEEK__[self.now.weekday()]
        self.year = "Year 1" if self.now.year % 2 == 0 else "Year 2"

    def text_general(self):
        day_dig = str(self.day)
        d_zero = int(day_dig[0])
        d_one = None if len(day_dig) == 1 else int(day_dig[1])
        day_emj = self.__DATE_EMJ__[d_zero] if len(day_dig) == 1 else "{}{}".format(self.__DATE_EMJ__[d_zero],
                                                                                    self.__DATE_EMJ__[d_one])
        row_1 = "\n{}, {} {}".format(self.dow, day_emj, self.__MONTH_NAMES__[self.month])
        row_2 = "{} Cьогодні читаємо:".format(self.__PRAY__)
        return row_1, row_2

    def today_we_read(self):
        today_reading = self.__TWO_YEAR_PLAN__[self.year][str(self.month)][str(self.day)]
        book_only_letters = []
        for item in today_reading:
            if item.strip()[0].isalpha():
                book_only_letters.append(re.sub(r"[^а-яіїєІ'ЇЄА-я]", ' ', item).strip())
            else:
                book_only_letters.append(' '.join(item.split()[:-1]).strip())
        transl_book = [self.__TRANSLATED_BOOK__[i] for i in book_only_letters]
        ukr_name_book = [' '.join(i.split()[:-1]).strip() for i in today_reading]
        chapters = [i.split()[-1] for i in today_reading]
        return today_reading, transl_book, ukr_name_book, chapters

    def bible_link(self, today_reading, transl_book, chapters):
        bible_link_list, bible_link_en = [], []
        bible_link_ge, bible_link_ru, bible_link_pl = [], [], []
        for book, ukr_book, chap in zip(transl_book, today_reading, chapters):
            bible_link_list.append(
                self.__BIBLE_LINK_TEMP__.format(
                    book, chap,
                    ';'.join(self.__BIBLE_VERSIONS__),
                    ukr_book
                )
            )
            eng_form = self.__ENGL_T_TRANS__[book]
            bible_list_en = self.bible_list(
                                                self.__BIBLE_LINK_TEMP__, self.__BIBLE_VERSIONS_ENG__,
                                                eng_form, chap
                                            )

            rus, germ, pol = self.__RUS_ENG__[eng_form], self.__GE_ENG__[eng_form], self.__PL_ENG__[eng_form]
            bible_list_ge = self.bible_list(self.__BIBLE_LINK_TEMP__, self.__BIBLE_VERSIONS_GE__, germ, chap)
            bible_list_pl = self.bible_list(self.__BIBLE_LINK_TEMP__, self.__BIBLE_VERSIONS_PL__, pol, chap)
            bible_list_ru = self.bible_list(self.__BIBLE_LINK_TEMP__, self.__BIBLE_VERSIONS_RUS__, rus, chap)

            bible_link_en.append(bible_list_en)
            bible_link_ge.append(bible_list_ge)
            bible_link_ru.append(bible_list_ru)
            bible_link_pl.append(bible_list_pl)

        len_mltlng = max(
                            [
                                self.len_message(i)
                                for i in [bible_link_en, bible_link_ge, bible_link_ru, bible_link_pl, bible_link_list]
                            ]
                        ) + 2

        bible_link_en = self.add_t_str(bible_link_en, len_mltlng)
        bible_link_ru = self.add_t_str(bible_link_ru, len_mltlng)
        bible_link_ge = self.add_t_str(bible_link_ge, len_mltlng)
        bible_link_pl = self.add_t_str(bible_link_pl, len_mltlng)
        bible_link_list = self.add_t_str(bible_link_list, len_mltlng)

        return bible_link_list, (bible_link_en, bible_link_ge, bible_link_ru, bible_link_pl)

    def shape_message(self):
        row_1, row_2 = self.text_general()
        intro_message = "{} {}".format(row_1, row_2)

        today_reading, transl_book, ukr_name_book, chapters = self.today_we_read()

        bible_link_list, bibles_mlt_ling = self.bible_link(today_reading, transl_book, chapters)
        bible_link_en, bible_link_ge, bible_link_ru, bible_link_pl = bibles_mlt_ling

        links = self.link_f_audio(ukr_name_book, chapters)
        print(ukr_name_book, chapters)
        links_drama = self.link_f_audio_drama(ukr_name_book, chapters)
        print('##', links_drama)

        bible_read_message = ['  '.join([self.__UA__, i]) for i in bible_link_list]

        audio_listen_message = [' '.join([self.__AUDIO__, i]) for i in links]
        if links_drama:
            audio_listen_drama = [' '.join([self.__THEATER__, i]) if bool(i) else "" for i in links_drama]
            audio_listen_message = ["{}  {}".format(audio_listen_message[i], audio_listen_drama[i]) for i in range(len(audio_listen_message))]

        bible_read_mes_en = "".join(['  '.join([self.__GB__, i]) for i in bible_link_en])
        bible_read_mes_ru = "".join(['  '.join([self.__RU__, i]) for i in bible_link_ru])
        bible_read_mes_ge = "".join(['  '.join([self.__GE__, i]) for i in bible_link_ge])
        bible_read_mes_pl = "".join(['  '.join([self.__PL__, i]) for i in bible_link_pl])


        bible_read_listen_ukr = '\n\n'.join(
                                                [
                                                    "{}{}".format(i, j) for i, j in
                                                    zip(bible_read_message, audio_listen_message)
                                                ]
                                            )
        full_message = "{}\n\n{}\n\n{}\n{}\n{}\n{}\n".format(
                                                                intro_message,
                                                                bible_read_listen_ukr,
                                                                bible_read_mes_en,
                                                                bible_read_mes_ge,
                                                                bible_read_mes_ru,
                                                                bible_read_mes_pl
                                                            )

        return full_message

    def test_message(self):
        decorator = "###   РІК 2  #### \n" + "# - " * 6
        year_n = 'Year 2'

        month = [
            self.__TEST_DAYS__ if num + 1 not in self.__THIRTY_DAYS_MONTH__ else self.__TEST_DAYS__[:-1]
            for num, i in enumerate(self.__TEST_MONTH__)
        ]
        month = [i if num != 1 else i[:-2] for num, i in enumerate(month)]

        full_message_list = []
        self.year = 'Year 2'
        for num, mon in enumerate(month):
            if num > 2:
                full_message_list.append("{}\n{}\n{}".format(decorator, self.__MONTH_NAMES__[num + 1], decorator))
                for day in mon:
                    if day > 11:
                        self.day = day
                        self.month = num + 1
                        row_1 = "{} {} {}".format(
                            self.__PRAY__,
                            "{}, {}   {}".format(year_n, str(self.day),
                                                 self.__MONTH_NAMES__[self.month]),
                            self.__PRAY__
                        )
                        intro_message = "{} \n".format(row_1)

                        today_reading, transl_book, ukr_name_book, chapters = self.today_we_read()
                        bible_link_list, bible_link_list_eng = self.bible_link(today_reading, transl_book, chapters)
                        links = self.link_f_audio(ukr_name_book, chapters)

                        bible_read_message = '\n'.join([' '.join([self.__BIBLE__, i]) for i in bible_link_list])
                        audio_listen_message = '\n'.join([' '.join([self.__AUDIO__, i]) for i in links])

                        bible_read_message_eng = '\n'.join([' '.join([self.__BIBLE__, i]) for i in bible_link_list_eng])
                        full_message = "{}\n{}  {}\n{}".format(
                            intro_message, bible_read_message, audio_listen_message, bible_read_message_eng)
                        full_message_list.append(full_message)
        return full_message_list

    def link_f_audio(self, ukr_name_book, chapters):
        if ukr_name_book[0] == 'Малахії':
            ukr_name_book, chapters = ukr_name_book[:-1], chapters[:-1]
        link_refs = [self.__AUDIO_CHAPTERWISE__[bk][ch] for bk, ch in zip(ukr_name_book, chapters)]
        audio_list = []
        for link, bk, ch in zip(link_refs, ukr_name_book, chapters):
            audio_list.append(self.__AUDIO_LINK_TEMP__.format(link, "{} {}".format(bk, ch)))
        return audio_list

    def link_f_audio_drama(self, ukr_name_book, chapters):

        audio_list = []
        for bk, ch in zip(ukr_name_book, chapters):
            if bk in self.__NT_BOOK__.keys():
                audio_list.append(self.__AUDIO_DRAMA_TEMP__.format(self.__TRANSLATED_BOOK__[bk], ch, "{} {}".format(bk, ch)))
            else:
                audio_list.append("")

        return audio_list

    @staticmethod
    def add_t_str(mes_l, add_str):
        return [i + " "*(add_str - len(i)) for i in mes_l]

    @staticmethod
    def len_message(mes_list):
        return max([len(i) for i in mes_list])

    @staticmethod
    def bible_list(bible_link_tem, bible_version, book, chap):

        links_bible = bible_link_tem.format(book, chap, ";".join(bible_version), "{} {}".format(book, chap))

        # links_bible = self.__BIBLE_LINK_TEMP__.format(book, chap, ";".join(self.__BIBLE_VERSIONS_ENG__),
        #                             "{} {}".format(book, chap))
        return links_bible

    def bot_test_message(self):
        test_messsages_list = self.test_message()
        for num, test_message in enumerate(test_messsages_list):
            time.sleep(60)
            if num % 19 == 0 and num != 0:
                time.sleep(60)
            try:
                bot = telegram.Bot(token=self.__TOKEN__)
                bot.send_message(chat_id=self.__LINK__, text=test_message, parse_mode=telegram.ParseMode.HTML)
            except telegram.error.RetryAfter:
                time.sleep(60)
                bot = telegram.Bot(token=self.__TOKEN__)
                bot.send_message(chat_id=self.__LINK__, text=test_message, parse_mode=telegram.ParseMode.HTML)
                time.sleep(60)

    def bot_send_message(self):
        full_message = self.shape_message()
        bot = telegram.Bot(token=self.__TOKEN__)
        status = bot.send_message(
                                    chat_id=self.__LINK__,
                                    text=full_message,
                                    parse_mode=telegram.ParseMode.HTML,
                                    disable_web_page_preview=True
                                    )
        print(status)


if __name__ == "__main__":
    get_bot = TelegramBibleReading()
    get_bot.bot_send_message()
