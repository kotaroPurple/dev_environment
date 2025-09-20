# src_4th 設計メモ

`src_3rd` から最終的な `src/dev_environment` とほぼ同等の機能へ辿り着くため、`src_4th` では以下を取り入れます。

## 目的
- `BaseTimeSeries` に近い多次元データ対応と不変性を導入
- `StreamDataset`/`StreamDataLoader` と同等の抽象化を体験
- `PipelineOrchestrator` の ErrorPolicy, Monitoring, BlockBuffer の活用を再現
- テストのサンプルを追加し、学習段階でテストの必要性を理解する

## 主な機能差分 (src_3rd → src_4th)
| 項目 | src_3rd | src_4th |
|------|---------|---------|
| データ構造 | 1D 限定 TimeSeriesBlock | 多次元可能 BaseTimeSeries ライクな dataclass |
| DataLoader | 逐次 yield のみ | StreamDataset + Collate + StreamDataLoader 的構造 |
| ノード | ProcessingNode ベース (状態あり) | Input/Output キー管理と Type check を強化 |
| Pipeline | ErrorPolicy なし | STOP / CONTINUE + PipelineExecutionError + Monitor |
| Monitor | block start/end | block/node start/end + duration 計測 |
| テスト | なし | pytest サンプル (data, io, pipeline) |

## ディレクトリ構成 (想定)
```
src_4th/
  __init__.py
  data/
    __init__.py, base.py, buffer.py
  io/
    __init__.py, adapters.py, dataset.py, dataloader.py, collate.py
  nodes.py
  pipeline.py
  monitoring.py
  quickstart.py
  tests/
    conftest.py, test_data.py, test_pipeline.py
```

## 割り切り
- この段階でも依存解決は DAG 前提・トポロジカルソートだが、最終版より簡略化
- モニタリングは `ConsoleMonitor` のみ、人間がログを読んで理解できる程度
- ErrorPolicy は STOP / CONTINUE のみ
- Dataset/Loader は同期処理のみ (マルチスレッドなし)

## 最終実装との違い
- 実際の `src/dev_environment` よりはコンパクトな実装に留める (クラス・メソッド数を少なく)
- `pydantic` や `numpy.typing` などハードな制約は導入せず、必要最低限の型ヒントにとどめる
- BlockBuffer も簡素化し、実装を追いやすいようコメントを豊富に残す
