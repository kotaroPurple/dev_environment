# src_2nd 設計メモ

`src_1st` の最小実装を拡張し、最終的な `src/dev_environment` へ繋がる概念を少しずつ導入します。以下の要素を追加します。

## 目的
- ブロックを dataclass で表現し、メタ情報 (タイムスタンプやサンプルレート) を持たせる
- 複数処理ノードを直列接続できるようにする (しかしグラフ依存解決は持たない)
- データローダ / パイプライン / ノードクラスを簡易的に導入し、概念の橋渡しを行う

## 仕様
- データコンテナ: `TimeSeriesBlock` (dataclass)
  - `values: np.ndarray`
  - `sample_rate: float`
  - `timestamp: datetime`
  - `metadata: dict[str, Any]`
- データローダ: `SimpleDataLoader`
  - `iter_blocks()` のようなジェネレーターから `TimeSeriesBlock` を逐次取得
- ノード: `BaseNode` 抽象クラス
  - `process(block: TimeSeriesBlock) -> TimeSeriesBlock`
  - `NormalizerNode`, `MovingAverageNode` の 2 種類を提供
- パイプライン: `SequentialPipeline`
  - コンストラクタにノードのリストを渡し、順番に `process` を呼ぶ
  - `run(blocks)` でブロックを1つずつ流し込んで結果を yield する

## ディレクトリ構成 (想定)
```
src_2nd/
  __init__.py
  data.py           # TimeSeriesBlock 定義と補助関数
  loader.py         # SimpleDataLoader
  nodes.py          # BaseNode と実装ノード
  pipeline.py       # SequentialPipeline
  main.py           # 実行例
```

## 割り切り
- 依存関係の解決は不要 (登録順に直列適用)
- エラー処理は最小限 (例外が発生したら停止)
- モニタリング・ログ出力は不要
- ブロック単位の処理に限定し、複数キーやバッファ共有は扱わない

## 将来の発展
- `src/dev_environment` での `ProcessingNode`/`PipelineBuilder`/`PipelineOrchestrator` への移行
- 複数キーの入出力や依存関係解決、エラーポリシーの導入
