# dev-environment

組み込みを意識した逐次オンライン処理パイプラインの実験的ライブラリです。PyTorch の `Dataset`/`DataLoader` に着想を得つつ、1 ブロック処理ごとに次のブロックを読み出す単一スレッド構成を実現します。

## クイックスタート

```bash
uv sync
source .venv/bin/activate
uv run python -m dev_environment.quickstart
```

`quickstart` モジュールでは以下を示します。

1. `StreamDataset` のモック実装でセンサーデータを模擬。
2. `StreamDataLoader` が 1 ブロックずつデータを供給。
3. `PipelineOrchestrator` が正規化などの `ProcessingNode` を逐次実行。

## 開発ルール

- 依存は `uv add` / `uv add --dev` で管理
- 品質は `ruff` にて `E`, `F`, `W`, `I` を対象に lint
- 行長は 100 文字まで、関数間は 2 行確保

詳細は `docs/` 以下の要求仕様・設計資料・データフロー図・タスクを参照してください。
