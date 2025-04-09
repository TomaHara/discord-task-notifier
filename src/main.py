import sys
import os
import argparse
from datetime import datetime
import pytz
import dotenv

# .envファイルから環境変数を読み込む
dotenv.load_dotenv()

# 自作モジュールのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fetchEvent import fetch_upcoming_events, format_event_time
from sendMessage import send_discord_message

def create_event_embeds(events, hours_ahead):
    """イベントリストからDiscord用の埋め込みメッセージを作成する"""
    if not events:
        return [{
            "title": "📚 課題通知",
            "description": f"{hours_ahead}時間以内に予定されている課題はありません。",
            "color": 5793266  # 緑色
        }]
    
    # 現在の日本時間
    now = datetime.now(pytz.timezone('Asia/Tokyo'))
    now_str = now.strftime("%Y年%m月%d日 %H:%M")
    
    # Moodle URL
    moodle_url = "https://lms.omu.ac.jp/"
    
    embeds = [{
        "title": "📚 課題通知",
        "description": f"現在時刻: {now_str}\n以下の課題の提出期限が近づいています！\n🔗 [Moodleサイトを開く]({moodle_url})",
        "color": 15105570,  # オレンジ色
        "footer": {
            "text": "Moodleカレンダー連携Bot"
        }
    }]
    
    # 最大10件までのイベントを埋め込み（Discordの制限）
    for event in events[:10]:
        deadline = format_event_time(event['start_time'])
        
        # 科目名とコード（カテゴリ）から情報を抽出
        subject_info = event['category'].split(' ', 1)
        # subject_code = subject_info[0] if len(subject_info) > 0 else ""
        subject_name = subject_info[1] if len(subject_info) > 1 else event['category']
        
        # タイトルから課題名を抽出（「」で囲まれた部分を取得）
        import re
        task_title = re.search(r'「(.+?)」', event['summary'])
        task_title = task_title.group(1) if task_title else event['summary']
        
        # 残り時間の計算
        time_until = event['start_time'] - datetime.now(pytz.UTC)
        hours_until = time_until.total_seconds() / 3600
        
        # 残り時間に応じて色を変更
        if hours_until <= 12:
            color = 15158332  # 赤色 (期限まで12時間以内)
            time_emoji = "⚠️"
        elif hours_until <= 24:
            color = 16776960  # 黄色 (期限まで24時間以内)
            time_emoji = "⏰"
        else:
            color = 3447003  # 青色 (それ以外)
            time_emoji = "🗓️"

        # イベントごとの埋め込み
        embed = {
            "title": f"📖 {subject_name}",
            "description": (
                f"**課題タイトル**\n"
                f"{task_title}\n"
                f"{time_emoji} **提出期限**\n"
                f"{deadline}\n"
            ),
            "color": color,
            "fields": []
        }
        
        # 説明があれば追加（長すぎる場合は省略）
        if event['description']:
            desc = event['description']
            if len(desc) > 200:
                desc = desc[:197] + "..."
            embed["fields"].append({
                "name": "📝 補足情報",
                "value": desc,
                "inline": False
            })
        
        embeds.append(embed)
    
    # イベント数が10件を超える場合
    if len(events) > 10:
        embeds.append({
            "description": f"*...他 {len(events) - 10} 件の課題があります*",
            "color": 10197915  # グレー
        })
    
    return embeds

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='MoodleカレンダーのイベントをDiscordに通知します')
    parser.add_argument('--ics', help='MoodleカレンダーのICS URL (.envファイルの設定を上書き)')
    parser.add_argument('--webhook', help='DiscordのWebhook URL (.envファイルの設定を上書き)')
    parser.add_argument('--hours', type=int, help='何時間先までのイベントを取得するか (.envファイルの設定を上書き)')
    parser.add_argument('--username', help='DiscordのBot表示名 (.envファイルの設定を上書き)')
    parser.add_argument('--avatar', help='DiscordのBotアバターURL (.envファイルの設定を上書き)')
    
    args = parser.parse_args()
    
    # 環境変数から設定を読み込む（コマンドライン引数があれば上書き）
    ics_url = args.ics or os.getenv('MOODLE_ICS_URL')
    webhook_url = args.webhook or os.getenv('DISCORD_WEBHOOK_URL')
    hours_ahead = args.hours or int(os.getenv('HOURS_AHEAD', '48'))
    username = args.username or os.getenv('BOT_USERNAME', 'イベント通知Bot')
    avatar_url = args.avatar or os.getenv('BOT_AVATAR_URL', '')
    
    if not ics_url:
        print("エラー: MoodleカレンダーのICS URLが指定されていません。")
        print("--icsオプションか.envファイルのMOODLE_ICS_URLで指定してください。")
        sys.exit(1)
        
    if not webhook_url:
        print("エラー: DiscordのWebhook URLが指定されていません。")
        print("--webhookオプションか.envファイルのDISCORD_WEBHOOK_URLで指定してください。")
        sys.exit(1)
    
    # イベント取得
    print(f"Moodleカレンダーからイベントを取得中...")
    events = fetch_upcoming_events(ics_url, hours_ahead)
    print(f"{len(events)}件のイベントが見つかりました")
    
    # 埋め込みメッセージ作成
    embeds = create_event_embeds(events, hours_ahead)
    
    # Discord送信
    print(f"Discordに通知を送信中...")
    success = send_discord_message(
        webhook_url=webhook_url,
        content="",  # 埋め込みを使うのでコンテンツは空
        username=username,
        avatar_url=avatar_url,
        embeds=embeds
    )
    
    if success:
        print("通知の送信に成功しました")
    else:
        print("通知の送信に失敗しました")
    
if __name__ == "__main__":
    # テスト用コード
    from fetchEvent import fetch_upcoming_events
    from sendMessage import send_discord_message

    # 環境変数を読み込む
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # 必要な設定を取得
    ics_url = os.getenv('MOODLE_ICS_URL')
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    username = os.getenv('BOT_USERNAME', 'テスト通知Bot')
    avatar_url = os.getenv('BOT_AVATAR_URL', '')
    hours_ahead = int(os.getenv('HOURS_AHEAD', '48'))

    if not ics_url or not webhook_url:
        print("エラー: 必要な環境変数が設定されていません。")
    else:
        # 課題情報を取得
        events = fetch_upcoming_events(ics_url, hours_ahead)
        print(f"取得した課題数: {len(events)}")

        # 通知メッセージを作成
        embeds = create_event_embeds(events, hours_ahead)

        # Discordに送信
        success = send_discord_message(
            webhook_url=webhook_url,
            content="",
            username=username,
            embeds=embeds
        )

        if success:
            print("通知を送信しました。")
        else:
            print("通知の送信に失敗しました。")