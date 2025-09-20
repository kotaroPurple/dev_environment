# データフロー図

## 全体フロー
プロジェクトにおけるデータ供給から結果出力までの経路を示します。

```mermaid
flowchart LR
    ext[外部データソース] --> adapter[DataSourceAdapter]
    adapter --> dataset[StreamDataset]
    dataset --> loader[StreamDataLoader]
    loader --> orchestrator[PipelineOrchestrator]
    orchestrator --> nodeA[ProcessingNode A]
    orchestrator --> nodeB[ProcessingNode B]
    nodeA --> orchestrator
    nodeB --> orchestrator
    orchestrator --> sink[DataSinkAdapter]
    orchestrator -.->|次ブロック要求| loader
    subgraph DatasetLayer
        dataset
    end
    subgraph LoaderLayer
        loader
    end
    subgraph ProcessingLayer
        orchestrator
        nodeA
        nodeB
    end
    subgraph Output
        sink
    end
```

- `StreamDataset` がブロック単位でデータを保持・提供し、`StreamDataLoader` が同期的に 1 ブロックずつ供給します。
- `PipelineOrchestrator` は処理ノードの依存を解決し、結果を `DataSinkAdapter` に引き渡します。

## ブロック処理シーケンス
1 ブロックが処理される際のシーケンスを示します。

```mermaid
sequenceDiagram
    participant Source as 外部ソース
    participant Adapter as DataSourceAdapter
    participant Dataset as StreamDataset
    participant Loader as StreamDataLoader
    participant Orchestrator as PipelineOrchestrator
    participant Nodes as ProcessingNode[*]
    participant Sink as DataSinkAdapter

    loop 各ブロック
        Orchestrator ->> Loader: 次ブロック要求
        Loader ->> Dataset: ブロック取得要求
        Dataset ->> Adapter: 次ブロック取得
        Adapter ->> Source: 生データ要求
        Source -->> Adapter: 生データ提供
        Adapter -->> Dataset: ブロックを返却
        Dataset -->> Loader: ブロックを返却
        Loader -->> Orchestrator: ブロックを受け渡し
        Orchestrator ->> Nodes: 依存解決後に処理を実行
        Nodes -->> Orchestrator: 処理結果/メトリクス
        Orchestrator ->> Sink: 出力を転送
    end
```

- 各ブロックの処理完了後に次ブロックが要求されるため、処理時間が直接スループットを決定します。
- 例外発生時は `PipelineOrchestrator` がポリシーに従い停止/継続を制御します。
