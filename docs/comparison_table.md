# 実装比較表

| 項目 | src_1st | src_2nd | src/dev_environment |
|------|---------|---------|---------------------|
| データ構造 | `numpy.ndarray` のみ | `TimeSeriesBlock` dataclass (1D 限定) | `BaseTimeSeries` (多次元対応・メタ情報豊富) |
| データローダ | `iter_blocks` ジェネレーター | `SimpleDataLoader` (事前生成ブロック) | `StreamDataset` + `StreamDataLoader` (抽象化 + アダプタ) |
| 処理ノード | 関数 (`normalize`) | `BaseNode` 継承 (Normalizer, MovingAverage) | `ProcessingNode` プロトコル (多出力・依存関係) |
| パイプライン制御 | ループ内で関数適用 | `SequentialPipeline` (直列のみ) | `PipelineBuilder` + `PipelineOrchestrator` (依存解決, ブロック毎制御) |
| エラー処理 | なし | なし (例外で停止) | `ErrorPolicy` (STOP/CONTINUE) + `PipelineExecutionError` |
| モニタリング | なし | なし | `PipelineMonitor` (ConsoleMonitor 等) |
| ブロック共有 | 不可 (単一処理) | 不可 (単一キー) | 可能 (`BlockBuffer` で複数キー共有) |
| サンプル実行 | `uv run python -m src_1st.main` | `uv run python -m src_2nd.main` | `uv run python -m dev_environment.quickstart` |
| テスト | なし | なし | `pytest` によるユニット/結合テスト |
| 主な目的 | コンセプト把握 (逐次処理) | dataclass &複数ノード導入 | 実運用向けフレームワーク |
