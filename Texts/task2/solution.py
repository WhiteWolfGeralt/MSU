import re

SENTENCES_REGEXP = r'(?P<sentence>([А-Я].*:\s*(\d+\.[^;]*;\s*)+(\d+\.[^\.]*\.\s*))|[А-Я].*:\n|(([А-Я]|\d+\.?)[^\.]*(\.|\n)?))'
PERSONS_REGEXP = r'(?P<person>\b[А-Я][а-я]+ ([А-Я][а-я]+)+\b)'

par_base = r'({.}|\(.\)|\[.\])*'
def make_par(res, depth):
    if depth == 1:
        return res.replace('.', '')
    res = res.replace('.', par_base)
    return make_par(res, depth - 1)
PARENTHESIS_REGEXP = make_par(par_base, 7)

ser_name = r"<h1.*><a.*href=\"/series/\d*/\">(?P<name>.*)</a></h1>"
ser_episodes_count = r"<td.*><b>Эпизоды:</b></td>((.|\n)*)<td.*>(?P<episodes_count>\d+)</td>"
ser_season = r"<td.*>Сезон (?P<season>\d+)</h1>(.|\n)*?(?P<season_year>\d+), эпизодов: (?P<season_episodes>\d+)(.|\n)*?</td>"
ser_episode = r"<span.*>Эпизод (?P<episode_number>\d+)</span><br/>\s*<h1.*><b>(?P<episode_name>.*)</b></h1>\s*(<span.*>(?P<episode_original_name>.*)</span>\s*</td>)?"
ser_list = [ser_name, ser_episodes_count, ser_season, ser_episode]
SERIES_REGEXP = "|".join(ser_list)

if __name__ == '__main__':
    entities = list()
    f = open("example2.txt", "r")
    html = f.read()
    regexp = "|".join(ser_list)
    for match in re.finditer(regexp, html):
        for key, value in match.groupdict().items():
            if value is not None:
                start, end = match.span(key)
                entities.append(f'"{value}" ({key})')
    for entity in entities:
        print(entity)
