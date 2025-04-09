# Moodle 課題通知 Bot

Moodle の課題提出期限を自動的に取得し、Discord に通知するボットです。設定した時間内に提出期限が近づいている課題を定期的にチェックし、分かりやすい形式で Discord チャンネルに通知します。

## 主な機能

- Moodle カレンダーの ics 形式の URL から課題情報を自動取得
- 設定した時間内（デフォルト：48 時間）に提出期限が近づいている課題を抽出
- 課題の重要度に応じた色分け表示（赤：12 時間以内、黄：24 時間以内、青：それ以上）
- 課題名、科目名、提出期限、補足情報などを見やすく表示
- 定期実行による自動通知（schedule_notify.py を使用）

## インストール方法

### 必要条件

- Python 3.8 以上
- pip パッケージ管理ツール

### セットアップ手順

1. リポジトリをクローンする

   ```
   git clone https://github.com/yourusername/discord-task-notifier.git
   cd discord-task-notifier
   ```

2. 必要なパッケージをインストールする

   ```
   pip install -r requirements.txt
   ```

3. 環境変数を設定する（`.env`ファイルの作成）
   ```
   MOODLE_ICS_URL=https://lms.example.com/calendar/export.php?... # MoodleカレンダーのicsエクスポートURL
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... # DiscordのWebhook URL
   HOURS_AHEAD=48 # 何時間先までの課題を通知するか
   BOT_USERNAME=課題通知Bot # Botの表示名
   BOT_AVATAR_URL=https://example.com/avatar.png # Botのアイコン画像URL（任意）
   ```

## 使用方法

### 単発実行

```bash
python src/main.py
```

コマンドラインオプション:

- `--ics` - Moodle カレンダーの ICS URL（.env ファイルの設定を上書き）
- `--webhook` - Discord の Webhook URL（.env ファイルの設定を上書き）
- `--hours` - 何時間先までのイベントを取得するか（.env ファイルの設定を上書き）
- `--username` - Discord の Bot 表示名（.env ファイルの設定を上書き）
- `--avatar` - Discord の Bot アバター URL（.env ファイルの設定を上書き）

### 定期実行

```bash
python src/schedule_notify.py
```

設定した時間間隔で自動的に通知を行います。デフォルトでは 6 時間ごとに実行されます。

## ファイル構成

- `main.py` - メインの実行ファイル
- `fetchEvent.py` - Moodle からイベント情報を取得する機能
- `sendMessage.py` - Discord にメッセージを送信する機能
- `schedule_notify.py` - 定期的な通知実行を管理
- `last_check.json` - 最後にチェックした時刻を記録するファイル
- `test_fetch.py` - イベント取得機能のテスト用ファイル

## カスタマイズ

通知の頻度や表示形式は、ソースコード内で簡単にカスタマイズできます。

- 通知頻度: `schedule_notify.py`内の設定を変更
- 表示色や形式: `main.py`内の`create_event_embeds`関数を編集

## トラブルシューティング

- ICS URL が無効: Moodle のカレンダーページから正しい ICS URL を再取得してください
- Webhook URL が無効: Discord サーバーの Webhook 設定を確認してください
- 通知が表示されない: `.env`ファイルの設定値を確認してください
