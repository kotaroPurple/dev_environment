# YWT 振り返り (src_1st → src_4th と最終実装)

## やったこと (Y)
- `src_1st` で 1 秒ブロックを逐次読み込み、単一処理だけを適用する最小例を実装
- `src_2nd` で dataclass (`TimeSeriesBlock`) と複数ノード・直列パイプラインを導入
- `src_3rd` でマルチキー対応と依存解決、状態付きノード (`SlidingWindowNode`/`ChunkingRMSNode`) を追加
- `src_4th` で最終実装に近い `BaseTimeSeries` や `StreamDataLoader`、ErrorPolicy、モニタリング、pytest テストを整備
- 最終ライブラリ `src/dev_environment` で抽象化・品質・モニタリング・テストを完備
- hands-on 資料・比較表・段階設計メモ (`docs/src_X_design.md`, `docs/hands-on.md`, `docs/comparison_table.md`) を作成

## わかったこと (W)
- ノードの `requires()`/`produces()` で依存関係を明示するとパイプラインの自律性が高まり、グラフ構造でも拡張しやすい
- バッファリングはノードの責務に明示的に組み込む方が、窓やチャンク処理を組み合わせやすい
- 状態付きノードを導入する際は `reset()` を忘れない、ErrorPolicy や Monitor で運用時の挙動が可視化される
- 段階別にサンプルを用意することで学習コストを抑えつつ、最終的な高度な抽象化を理解しやすくなる
- pytest によるユニット/結合テストを用意しておくと、状態付きノードやバッファ処理の回 regress を検知しやすい

## つぎにすること (T)
- `src/dev_environment` に SlidingWindow/ChunkingRMS など応用ノードを追加し、実運用ユースケースをカバー
- ベンチマークスクリプトを整備し、ブロック遅延やウィンドウ処理のパフォーマンスを測定
- hands-on をワークショップ形式で補強し、各ステップでの課題やチェックリストを拡充
- ErrorPolicy に PAUSE/RETRY など運用想定のバリエーションを追加検討
