# CamelCase Migration Guide

バックエンドで自動変換を実装したので、フロントエンドも段階的にキャメルケースに移行します。

## 完了したステップ

✅ バックエンド: `dispatcher.py`でリクエスト/レスポンスの自動変換を実装
✅ バックエンド: BFFエンドポイントにも変換を適用

## 移行ステップ

### フェーズ1: 型定義の更新 (推奨: 手動)

主要な型定義ファイルを更新:

1. `src/web/types/hyperparameters.ts`
   - `top_p` → `topP`
   - `top_k` → `topK`

2. `src/web/lib/api/session/getSession.ts` - `SessionDetail`型
   - `session_id` → `sessionId`
   - `multi_step_reasoning_enabled` → `multiStepReasoningEnabled`
   - `token_count` → `tokenCount`

3. APIレスポンス型の更新
   - `src/web/lib/api/session/startSession.ts`
   - `src/web/lib/api/session/forkSession.ts`
   - など

### フェーズ2: 自動変換スクリプト実行

```bash
# バックアップ
git add -A
git commit -m "Before camelCase conversion"

# 実行
./scripts/convert_to_camelcase.sh

# 型チェック
npm run typecheck
```

### フェーズ3: 手動修正

- APIリクエストボディのキー名は**そのまま**でOK（バックエンドで変換される）
- コメントや文字列リテラル内の不要な変換を戻す
- 型エラーを修正

### フェーズ4: テスト

```bash
npm test
npm run build
```

## 変換マップ

| Before (snake_case)          | After (camelCase)         |
| ---------------------------- | ------------------------- |
| session_id                   | sessionId                 |
| created_at                   | createdAt                 |
| updated_at                   | updatedAt                 |
| top_p                        | topP                      |
| top_k                        | topK                      |
| new_session_id               | newSessionId              |
| session_ids                  | sessionIds                |
| multi_step_reasoning_enabled | multiStepReasoningEnabled |
| token_count                  | tokenCount                |
| reference_index              | referenceIndex            |
| turn_index                   | turnIndex                 |
| fork_index                   | forkIndex                 |
| verifier_session_id          | verifierSessionId         |

## 注意点

### 変換不要な箇所

- コメント内のAPI仕様の説明
- テストデータのモック
- APIドキュメント参照

### 既に正しい箇所

バックエンドで変換されるため、**リクエストボディ**のキー名は:

- フロントエンド: キャメルケース送信 → バックエンド: 自動変換でスネークケース
- バックエンド: スネークケース返却 → フロントエンド: 自動変換でキャメルケース

そのため、APIクライアントのリクエスト/レスポンス型をキャメルケースに統一すれば完了です。
