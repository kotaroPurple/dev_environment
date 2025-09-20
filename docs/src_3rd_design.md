# src_3rd 設計メモ

`src_2nd` から最終的な `src/dev_environment` に近づけるため、以下の要素を追加した「第3段階」実装を想定します。

## 目的
- 複数キーの入出力とブロック共有 (`BlockBuffer` の簡易版) を導入
- ノードごとに `requires` / `produces` を宣言可能にし、パイプラインが依存関係を解決
- データローダを抽象化してアダプタに対応できるようにする
- モニタリングの入り口となるイベントフックを提供 (ログ出力は最小限)

## 仕様
- データ構造: `TimeSeriesBlock` (src_2nd のものを再利用/拡張)
- データローダ: `Dataset` + `DataLoader`
  - `Dataset` が `__iter__` と `__len__` を提供
  - `DataLoader` が逐次的にブロックを取り出す
- ノード: `ProcessingNode`
  - `requires() -> list[str]`
  - `produces() -> list[str]`
  - `process(inputs: dict[str, TimeSeriesBlock]) -> dict[str, TimeSeriesBlock]`
- パイプライン: `PipelineBuilder`/`Pipeline`
  - 依存関係をトポロジカルソートで解決
  - 各ブロック処理時に単純なモニタイベント (`on_block_start`, `on_block_end`) を呼び出す

## ディレクトリ構成
```
src_3rd/
  __init__.py
  data.py          # TimeSeriesBlock + BlockBuffer
  dataset.py       # Dataset 抽象 + IterableDataset 実装
  dataloader.py    # DataLoader (逐次取得)
  nodes.py         # ProcessingNode, NormalizerNode, MovingAverageNode, SplitNode 等
  pipeline.py      # PipelineBuilder, Pipeline, モニターフック
  monitor.py       # ConsoleMonitor (簡易版)
  main.py          # 実行例
```

## 割り切り
- ErrorPolicy は未実装 (例外発生で終了)
- モニタは標準出力にイベントを表示するだけ
- データローダは単一スレッド・プリフェッチなし
- 型安全性/型ヒントは最小限 (`TimeSeriesBlock` のみ扱う)

## 最終実装との違い
- `BaseTimeSeries` のような多次元対応や複雑なメタ情報管理は省略
- `PipelineExecutionError` や ErrorPolicy, BlockBuffer 多キー活用などは簡略化
- `StreamDataset`/`StreamDataLoader` ほど汎用ではないが、概念として近い構造
