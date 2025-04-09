import os
from dotenv import load_dotenv
from fetchEvent import fetch_upcoming_events, format_event_time
from pprint import pprint
import icalendar

def debug_ical_object(obj):
    """iCalendarオブジェクトの詳細情報を取得"""
    if isinstance(obj, icalendar.prop.vCategory):
        # vCategoryオブジェクトの場合、全ての属性を表示
        print("\n=== vCategory詳細情報 ===")
        print(f"Raw value: {obj}")
        print(f"Type: {type(obj)}")
        print(f"Parameters: {obj.params}")
        # 値を文字列として取得
        try:
            if hasattr(obj, 'cats'):
                print(f"Categories: {obj.cats}")
        except Exception as e:
            print(f"値の取得に失敗: {e}")
        
        # すべての属性を表示
        print("\nすべての属性:")
        for attr in dir(obj):
            if not attr.startswith('_'):  # プライベート属性以外を表示
                try:
                    value = getattr(obj, attr)
                    print(f"{attr}: {value}")
                except Exception as e:
                    print(f"{attr}: <取得エラー: {e}>")

def main():
    # .envファイルから設定を読み込む
    load_dotenv()
    
    # 環境変数から設定を取得
    ics_url = os.getenv('MOODLE_ICS_URL')
    hours_ahead = int(os.getenv('HOURS_AHEAD', '48'))
    
    if not ics_url:
        print("エラー: MOODLE_ICS_URLが.envファイルに設定されていません。")
        return
    
    print(f"=== Moodleカレンダーから{hours_ahead}時間以内のイベントを取得 ===\n")
    events = fetch_upcoming_events(ics_url, hours_ahead)
    
    if not events:
        print(f"指定期間内のイベントはありません。")
        return
        
    print(f"取得イベント数: {len(events)}件\n")
    print("=== 生データの表示（pprint） ===")
    pprint(events, width=120, sort_dicts=False)
    
    print("\n=== 整形済みデータの表示 ===")
    for i, event in enumerate(events, 1):
        print(f"\n[イベント {i}]")
        print(f"タイトル: {event['summary']}")
        print(f"開始時刻: {format_event_time(event['start_time'])}")
        
        # 終了時刻の表示
        if event['end_time']:
            print(f"終了時刻: {format_event_time(event['end_time'])}")
            
        if event['is_all_day']:
            print("※ 終日イベント")
        
        if event['description']:
            print(f"説明: {event['description']}")
        
        if event['location']:
            print(f"場所: {event['location']}")
            
        if event['url']:
            print(f"URL: {event['url']}")
            
        if event['categories']:
            print(f"カテゴリ: {', '.join(event['categories'])}")
            print("\nカテゴリ情報:")
            if isinstance(event['categories'], icalendar.prop.vCategory):
                debug_ical_object(event['categories'])
            else:
                print(f"カテゴリデータ: {event['categories']}")
                print(f"カテゴリデータ型: {type(event['categories'])}")
            
        if event['created']:
            print(f"作成日時: {format_event_time(event['created'])}")
            
        if event['last_modified']:
            print(f"最終更新: {format_event_time(event['last_modified'])}")
            
        if event['status']:
            print(f"ステータス: {event['status']}")
            
        print(f"イベントID: {event['uid']}")
        print(f"更新回数: {event['sequence']}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()