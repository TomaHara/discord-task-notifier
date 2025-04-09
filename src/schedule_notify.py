import os
from datetime import datetime
import pytz
from typing import List, Dict, Any
from dotenv import load_dotenv
from fetchEvent import fetch_upcoming_events, format_event_time
from sendMessage import send_discord_message

def create_daily_notification(events: List[Dict[str, Any]], hours_ahead: int) -> List[Dict[str, Any]]:
    """毎日の定期通知用の埋め込みメッセージを作成"""
    from main import create_event_embeds
    return create_event_embeds(events, hours_ahead)

def main(request=None):
    """
    メイン関数 - GCP Cloud Functionsのエントリポイントとして機能
    requestパラメータはCloud Functions用で、ローカル実行時は無視されます
    """
    # 環境変数の読み込み
    load_dotenv()
    ics_url = os.getenv('MOODLE_ICS_URL')
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    hours_ahead = int(os.getenv('HOURS_AHEAD', '48'))

    if not all([ics_url, webhook_url]):
        error_message = "必要な環境変数が設定されていません。"
        print(error_message)
        return {"error": error_message}, 500

    # 課題リストを取得
    print(f"Moodleカレンダーから{hours_ahead}時間以内のイベントを取得中...")
    events = fetch_upcoming_events(ics_url, hours_ahead)
    print(f"{len(events)}件の課題が見つかりました")
    
    # 埋め込みメッセージ作成
    embeds = create_daily_notification(events, hours_ahead)
    
    # Discord送信
    print(f"Discordに通知を送信中...")
    success = send_discord_message(
        webhook_url=webhook_url,
        content="",  # 埋め込みを使うのでコンテンツは空
        username=os.getenv('BOT_USERNAME', 'イベント通知Bot'),
        avatar_url=os.getenv('BOT_AVATAR_URL', ''),
        embeds=embeds
    )
    
    if success:
        print("通知の送信に成功しました")
        return {"status": "success", "message": f"{len(events)}件の課題を通知しました"}, 200
    else:
        print("通知の送信に失敗しました")
        return {"error": "通知の送信に失敗しました"}, 500

if __name__ == "__main__":
    # ローカル実行時はmain関数を直接呼び出す
    main()