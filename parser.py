import pandas as pd
import datetime as dt
import re
import json

def hour12to24(meridiem, hour: int) -> int:
    hour_24 = hour
    if meridiem == '오전' and hour == 12:
        hour_24 = hour_24 - 12
    elif meridiem == '오후' and 1 <= hour < 12:
        hour_24 = hour_24 + 12

    return hour_24


def attr(text):
    """picture, video, file, link, emoticon, text, largetext"""
    if re.search(r'(http|https|ftp):\/\/', text):
        return 'link'
    elif text == '이모티콘':
        return 'emoticon'
    elif text == '사진':
        return 'picture'
    elif text[:4] == '파일: ':
        return 'file'
    elif len(text)>100:
        return 'largetext'
    else:
        return 'text'



def parse_pc_kakaotalk(file):
    msg_p = re.compile(r'\[(.+?)\] \[(오전|오후) (\d{,2}):(\d{,2})\] (.*)$')
    date_p = re.compile(r' (\d{4})년 (\d{,2})월 (\d{,2})일 ')

    with open(file=file, mode='r', encoding='utf-8') as f:
        title = f.readline()
        title = title.replace(' 님과 카카오톡 대화\n', '')

        _ = f.readline()
        _ = f.readline()

        data = []
        ts = None
        while True:
            line = f.readline()
            if not line:
                break

            m1 = date_p.search(line)
            if m1:
                year, month, date = m1.groups()
                ts = dt.datetime(int(year), int(month), int(date))
                continue

            m2 = msg_p.search(line)
            if m2:
                user, meridiem, hour, minute, text = m2.groups()

                ts = ts.replace(hour=hour12to24(meridiem, int(hour)), minute=int(minute))
                data.append([ts, user, text])
                continue
            try:
                data[-1][-1] = data[-1][-1] + '\n' + line
            except Exception as e:
                pass

    df = pd.DataFrame(data=data, columns=['ts', 'user', 'text'])
    df = df.astype(dtype={'ts': 'datetime64', 'user': 'category'})
    # result = json(df.ts)
    return title, df


if __name__ == '__main__':
    file = './KakaoTalk.txt'
    title, df = parse_pc_kakaotalk(file=file)
    print(df.to_dict())
    df.info()