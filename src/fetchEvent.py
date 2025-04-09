import datetime
import requests
import os
from icalendar import Calendar, Event
from typing import List, Dict, Any
import pytz
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def fetch_upcoming_events(ics_url: str, hours_ahead: int = 48) -> List[Dict[str, Any]]:
    """
    Moodleカレンダーの.ics URLから指定時間内に予定されているイベントを取得する

    Args:
        ics_url (str): ICS形式のカレンダーURL
        hours_ahead (int, optional): 何時間先までのイベントを取得するか. デフォルトは48時間

    Returns:
        List[Dict[str, Any]]: イベント情報のリスト
    """
    try:
        # ICSファイルの取得
        response = requests.get(ics_url)
        response.raise_for_status()
        
        # iCalendarオブジェクトにパース
        cal = Calendar.from_ical(response.content)
        
        # 現在時刻の取得（UTC）
        now = datetime.datetime.now(pytz.UTC)
        
        # 終了時刻の計算（現在時刻から指定時間後）
        end_time = now + datetime.timedelta(hours=hours_ahead)
        
        upcoming_events = []
        
        # イベントの処理
        for component in cal.walk():
            if component.name == "VEVENT":
                # 基本情報の取得
                start_time = component.get('dtstart').dt
                end_time_event = component.get('dtend').dt if component.get('dtend') else None
                
                # 日付のみの場合は日時に変換
                if isinstance(start_time, datetime.date) and not isinstance(start_time, datetime.datetime):
                    start_time = datetime.datetime.combine(start_time, datetime.time.min)
                    start_time = pytz.UTC.localize(start_time)
                
                if isinstance(end_time_event, datetime.date) and not isinstance(end_time_event, datetime.datetime):
                    end_time_event = datetime.datetime.combine(end_time_event, datetime.time.max)
                    end_time_event = pytz.UTC.localize(end_time_event)
                
                # 現在時刻から指定時間内のイベントのみを抽出
                if now <= start_time <= end_time:
                    # 追加の情報を取得
                    uid = str(component.get('uid', ''))
                    sequence = str(component.get('sequence', '0'))
                    created = component.get('created').dt if component.get('created') else None
                    last_modified = component.get('last-modified').dt if component.get('last-modified') else None
                    status = str(component.get('status', ''))
                    
                    # カテゴリ（科目名）の取得
                    category_obj = component.get('categories')
                    category_name = get_category_name(category_obj) if category_obj else ""
                    
                    event = {
                        'summary': str(component.get('summary', 'イベント名なし')),
                        'start_time': start_time,
                        'end_time': end_time_event,
                        'description': str(component.get('description', '')),
                        'location': str(component.get('location', '')),
                        'url': str(component.get('url', '')),
                        'uid': uid,
                        'sequence': sequence,
                        'created': created,
                        'last_modified': last_modified,
                        'status': status,
                        'category': category_name,
                        'is_all_day': isinstance(component.get('dtstart').dt, datetime.date)
                    }
                    upcoming_events.append(event)
        
        # 開始時間順にソート
        upcoming_events.sort(key=lambda x: x['start_time'])
        
        return upcoming_events
    
    except Exception as e:
        print(f"イベント取得エラー: {e}")
        return []

def format_event_time(dt: datetime.datetime) -> str:
    """
    日時を日本語フォーマットに整形する

    Args:
        dt (datetime.datetime): フォーマットする日時

    Returns:
        str: フォーマットされた日時文字列
    """
    # 日本のタイムゾーンに変換
    japan_tz = pytz.timezone('Asia/Tokyo')
    dt_japan = dt.astimezone(japan_tz)
    
    # 曜日の日本語表記
    weekday_jp = ['月', '火', '水', '木', '金', '土', '日']
    weekday = weekday_jp[dt_japan.weekday()]
    
    # フォーマット: 2025年4月8日(火) 15:00
    return f"{dt_japan.year}年{dt_japan.month}月{dt_japan.day}日({weekday}) {dt_japan.hour:02}:{dt_japan.minute:02}"

def get_category_name(category) -> str:
    """
    vCategoryオブジェクトから科目名を取得する

    Args:
        category: vCategoryオブジェクト

    Returns:
        str: 科目名
    """
    if hasattr(category, 'cats'):
        # カテゴリリストの最初の要素を取得し、デコードして返す
        try:
            first_cat = category.cats[0]
            if hasattr(first_cat, 'encode'):
                # すでに文字列の場合
                return str(first_cat)
            # バイト文字列の場合はデコード
            return first_cat.decode('utf-8')
        except (IndexError, AttributeError):
            pass
    return ""

if __name__ == "__main__":
    # 環境変数から設定を読み込む
    ics_url = os.getenv('MOODLE_ICS_URL')
    hours_ahead = int(os.getenv('HOURS_AHEAD', '48'))
    
    if not ics_url:
        print("エラー: MOODLE_ICS_URLが.envファイルに設定されていません。")
        exit(1)
    
    events = fetch_upcoming_events(ics_url, hours_ahead)
    
    print(f"今後{hours_ahead}時間以内のイベント: {len(events)}件")
    
    for i, event in enumerate(events, 1):
        start_time_formatted = format_event_time(event['start_time'])
        print(f"[{i}] {event['summary']}")
        print(f"    日時: {start_time_formatted}")
        if event['location']:
            print(f"    場所: {event['location']}")
        if event['description']:
            print(f"    詳細: {event['description']}")
        if event['category']:
            print(f"    科目名: {event['category']}")
        print()