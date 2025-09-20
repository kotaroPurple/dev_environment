# ハンズオン: 段階的に理解する逐次処理パイプライン

このハンズオンでは `src_1st` → `src_2nd` → `src/dev_environment` の順で機能と抽象化を段階的に確認します。

## 前提
- `uv sync` 済み
- `uv run` でモジュールを実行できる環境

---

## ステップ1: src_1st (最小構成)
1. 実行: `uv run python -m src_1st.main`
2. コード確認: `src_1st/loader.py`, `src_1st/process.py`, `src_1st/main.py`
3. 演習: `process.normalize` を改造し、平均値も計算して表示する

ポイント:
- 1 次元 `numpy.ndarray` のみ扱い
- ノードや dataclass は未導入

---

## ステップ2: src_2nd (中間構成)
1. 実行: `uv run python -m src_2nd.main`
2. コード確認: `src_2nd/data.py`, `src_2nd/nodes.py`, `src_2nd/pipeline.py`
3. 演習:
   - `TimeSeriesBlock` に `sensor_id` メタ情報を追加して出力
   - `MovingAverageNode` の窓幅を変え、出力の変化を確認

ポイント:
- dataclass によるメタ情報管理
- ノードクラスによる責務分割
- 直列パイプラインによる複数処理の連結

---

## ステップ3: src/dev_environment (最終構成)
1. 実行: `uv run python -m dev_environment.quickstart`
2. コード確認: `src/dev_environment/data/`, `io/`, `pipeline/`
3. 演習:
   - 新しい `ProcessingNode` を作成し、`PipelineBuilder` に登録
   - `ErrorPolicy.CONTINUE` を試し、挙動を観察
   - `tests/` を参考にユニットテストを追加

ポイント:
- 複数キー管理 (`BlockBuffer`)
- 依存解決と順序決定 (`PipelineBuilder`)
- モニタリング/エラーポリシー (`PipelineOrchestrator`, `ConsoleMonitor`)

---

## 追加課題
- `src_1st` → `src_2nd` の差分を docstring やコメントで整理
- `src/dev_environment` に `src_2nd` のノードを移植し、互換性を保つための変更点をまとめる
- ベンチマークリポートを作成し、各段階での遅延を比較
