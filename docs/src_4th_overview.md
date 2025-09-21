# src_4th データフローとクラス概要

## データフロー
`src_4th` モジュール全体のデータフローを以下に示します。

```mermaid
digraph G {
    rankdir=LR
    subgraph cluster_io {
        label="I/O 層"
        style=dashed
        source["AdapterDataset\n(Callable/Iterable)"]
        loader["StreamDataLoader"]
    }
    subgraph cluster_pipeline {
        label="Pipeline 層"
        style=dashed
        builder["PipelineBuilder\n(依存解決)"]
        orchestrator["PipelineOrchestrator\n(ErrorPolicy/Monitor)"]
    }
    subgraph cluster_nodes {
        label="Processing Nodes"
        style=dashed
        nodeA["NormalizerNode"]
        nodeB["MovingAverageNode"]
        nodeC["SlidingWindowNode"]
    }
    monitor["ConsoleMonitor"]
    buffer["BlockBuffer"]
    data["BaseTimeSeries (values, sample_rate, timestamp, metadata)"]

    source -> loader -> orchestrator
    builder -> orchestrator
    orchestrator -> buffer
    buffer -> nodeA
    buffer -> nodeB
    buffer -> nodeC
    nodeA -> buffer
    nodeB -> buffer
    nodeC -> buffer
    orchestrator -> monitor
    loader -> data
    nodeA -> data
    nodeB -> data
    nodeC -> data
}
```

## クラスの役割

- **BaseTimeSeries (`src_4th/data/base.py`)**
  - Numpy 配列とサンプリング情報、メタ情報を持つ不変データクラス。`copy_with` で値やメタ情報を変えた新インスタンスを生成。

- **BlockBuffer (`src_4th/data/buffer.py`)**
  - パイプライン内で生成された `BaseTimeSeries` をキー付きで共有するシンプルなストア。

- **AdapterDataset / IterableDataset / StreamDataLoader (`src_4th/io/…`)**
  - 外部ソースを `BaseTimeSeries` に変換し、逐次的にパイプラインへ渡す。最終実装の `StreamDataset`/`StreamDataLoader` の簡易版。

- **ProcessingNode / NormalizerNode / MovingAverageNode / SlidingWindowNode (`src_4th/nodes.py`)**
  - ノードごとに `requires()`/`produces()` で依存関係を宣言し、`process()` で `BaseTimeSeries` を変換。`SlidingWindowNode` は内部バッファで窓を蓄積し、十分に溜まった時だけ出力。

- **PipelineBuilder / PipelineOrchestrator (`src_4th/pipeline.py`)**
  - ノード登録と依存解決、`ErrorPolicy` の適用、`BlockBuffer` の更新、モニタへのイベント送出など、逐次処理の中心ロジックを担う。

- **ConsoleMonitor (`src_4th/monitoring.py`)**
  - ブロック開始・終了・エラーを標準出力に記録し、処理時間や出力キーを可視化するシンプルなモニタ。

- **quickstart (`src_4th/quickstart.py`)**
  - サイン波データを生成し、正規化・移動平均・スライディングウィンドウ処理を行うサンプルエントリポイント。

- **tests (`src_4th/tests/…`)**
  - `BaseTimeSeries` の基本動作とパイプライン処理（エラーポリシー、スライディングウィンドウの挙動など）を pytest で検証するサンプル。
