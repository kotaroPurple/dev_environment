# 利用例 (組み込み逐次パイプライン)

組み込み向けのオンライン処理を想定したサンプル構成です。 `Quickstart` スクリプトでは以下を実演します。

1. `IterableDataSourceAdapter` がインメモリのセンサーデータを供給
2. `CollatedStreamDataset` がブロックを `BaseTimeSeries` に変換
3. `StreamDataLoader` が 1 ブロックずつ逐次取得
4. `PipelineOrchestrator` が正規化 (`NormaliseAmplitudeNode`) と移動平均 (`MovingAverageNode`) を実行
5. `ConsoleMonitor` が各ブロック/ノードの実行時間を記録

## 実行手順

```bash
uv sync
uv run python -m dev_environment.quickstart
```

出力例:

```
[quickstart] block 0 start
[quickstart] block 0 node NormaliseAmplitudeNode start
...
Block 0
  raw: shape=(32, 1), scale=None
  raw_norm: shape=(32, 1), scale=1.0
  raw_norm_ma5: shape=(32, 1), scale=1.0
```

## カスタマイズ

- ノードを追加する場合は `dev_environment.pipeline.ProcessingNode` を継承し、`requires()`/`produces()`/`process()` を実装します。
- データ供給源を差し替える場合は `dev_environment.io.DataSourceAdapter` を実装し、`CollatedStreamDataset` に渡します。
- 組み込みでのエラー許容度に応じて `PipelineBuilder.build(..., on_error=ErrorPolicy.CONTINUE)` を設定してください。

## テスト

ユニット/結合テストは以下で実行できます。

```bash
uv run pytest
```
