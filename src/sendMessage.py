import requests
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

def send_discord_message(webhook_url: str, 
                        content: str, 
                        username: Optional[str] = None, 
                        avatar_url: Optional[str] = None, 
                        embeds: Optional[list] = None) -> bool:
    """
    Discordの特定チャンネルにWebhookを使ってメッセージを送信する関数
    
    Args:
        webhook_url (str): DiscordのWebhook URL
        content (str): 送信するメッセージの内容
        username (Optional[str], optional): 表示するユーザー名. デフォルトはNone
        avatar_url (Optional[str], optional): 表示するアバターのURL. デフォルトはNone
        embeds (Optional[list], optional): 埋め込みメッセージ. デフォルトはNone
        
    Returns:
        bool: 送信成功したらTrue、失敗したらFalse
    """
    data: Dict[str, Any] = {}
    
    if content:
        data["content"] = content
    
    if username:
        data["username"] = username
        
    if avatar_url:
        data["avatar_url"] = avatar_url
        
    if embeds:
        data["embeds"] = embeds
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Discordへのメッセージ送信に失敗しました: {e}")
        return False

if __name__ == "__main__":
    # 環境変数から設定を読み込む
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    bot_username = os.getenv('BOT_USERNAME', 'テスト通知Bot')
    bot_avatar_url = os.getenv('BOT_AVATAR_URL', '')
    
    if not webhook_url:
        print("エラー: DISCORD_WEBHOOK_URLが.envファイルに設定されていません。")
        exit(1)
    
    message = "これはテストメッセージです"
    
    # 基本的なメッセージ送信
    send_discord_message(webhook_url, message)
    
    # ユーザー名とアバターを指定したメッセージ送信
    send_discord_message(
        webhook_url, 
        message, 
        username=bot_username, 
        avatar_url=bot_avatar_url
    )
    
    # 埋め込みメッセージを使った送信例
    embed = {
        "title": "イベント通知",
        "description": "48時間以内に予定されているイベントです",
        "color": 5814783,  # 色コード (青色)
        "fields": [
            {
                "name": "イベント名",
                "value": "テストイベント"
            },
            {
                "name": "日時",
                "value": "2025年4月10日 15:00"
            }
        ]
    }
    
    send_discord_message(
        webhook_url, 
        "", 
        username="イベント通知Bot", 
        embeds=[embed]
    )