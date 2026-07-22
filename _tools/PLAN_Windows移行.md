# Wandering Sword 翻訳パイプライン — Windowsローカル(Claude Code)移行計画

作成: 2026-06-15 / 状態: 計画(ツール導入は完了、コード修正は未着手)

## 背景
`_tools/` 一式は元々 **Linuxサンドボックス**(`/sessions/<id>/mnt/...`)向けに作られていた。
今後は **Windowsローカルの Claude Code** で動かす。そのための差分を整理する。

---

## A. 完了済み(2026-06-15 このチャットで実施)

| 項目 | 内容 |
|---|---|
| Python本体 | `Python.Python.3.12`(winget, user scope)導入。`%LOCALAPPDATA%\Programs\Python\Python312\python.exe` = **3.12.10**。外部パッケージ不要(全スクリプトが標準ライブラリのみ＝struct/json/glob/os/sys/re/argparse/subprocess/datetime/collections/shutil/tempfile)を実機確認済。 |
| repak | Windows版 `repak_cli 0.2.3` を `_tools/repak.exe` に配置。動作確認済。 |
| Obsidian | 導入済(ユーザー側)。 |
| git | 既存 2.54。 |
| Storeスタブ無効化 | アプリ実行エイリアスの python.exe/python3.exe を**オフ済**。素の `python` → `Python 3.12.10` を確認。 |
| 読み取り系の実走確認 | `python _tools/status.py` がネイティブで正常出力(スタブ時は無反応だった)。進捗 714/888キャラ・約38%。 |
| ゲーム実体 | `C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks` に実在を確認(`aaWanderingSword_JP_P.pak` 配置済)。 |

---

## B. 必須コード修正(Linux依存の解消)

### B-1. repak のパス(★最優先) — ✅ 完了 2026-06-15
拡張子なし `_tools/repak` を Windows の subprocess で呼ぶと、隣の **Linux版ELFバイナリ** を実行して
`WinError 193`(有効なWin32アプリでない)で落ちる。CreateProcessは既存ファイルがあると `.exe` を補完しない。

**対象**:
- `_tools/apply_char.py:15`
- `_tools/apply_proofread.py:15`
- `_tools/apply_translations.py:19`
- `_tools/deploy_to_game.py:13`
- 補助: `_tools/_tl_progexport.py:157`, `_tools/_tl_ui2.py`(相対 `'_tools/repak'` を使用)

**実施**: 下記を4ファイル(apply_char/apply_proofread/apply_translations/deploy_to_game)に適用済。
```python
REPAK = os.path.join(ROOT, "_tools", "repak.exe" if os.name == "nt" else "repak")
```
検証: subprocess経由で `repak_cli 0.2.3` 実行成功(WinError 193解消)、py_compile全OK。
※ Linux版ELF `_tools/repak` は残置(`os.name` 分岐で使い分け。Linux実行時の互換温存)。
※ 補助スクリプト `_tl_progexport.py` / `_tl_ui2.py`(予備・旧行順方式)は未対応。使う時に同様修正。

### B-2. ゲームフォルダ検出(`deploy_to_game.py` find_game_paks) — ✅ 完了 2026-06-15
現状 `/sessions/*/mnt/...` を glob しており Windows では常に None。

**修正案**: Windows分岐を追加。確認済みの実パスを先頭に。
```python
def find_game_paks():
    if os.name == "nt":
        cands = [
            r"C:\Program Files (x86)\Steam\steamapps\common\Wandering Sword\Wandering_Sword\Content\Paks",
            # 別ライブラリに入れている場合はここに追記
        ]
        for c in cands:
            if os.path.isdir(c):
                return c
        return None
    # 既存のLinux glob はそのまま(else側に残す)
    ...
```

### B-3. `/tmp` のハードコード(`deploy_to_game.py` 自己検証) — ✅ 完了 2026-06-15
`vdir = "/tmp/_deployverify"` がLinux前提で、**WS_TMP非対応**(下記B-4と違いここは環境変数を見ない)。

**修正案**: WS_TMP優先＋`tempfile`フォールバック。
```python
import tempfile
base = os.environ.get("WS_TMP", tempfile.gettempdir())
vdir = os.path.join(base, "_deployverify")
```

### B-4. WS_TMP 規約(中間ファイルの置き場所 — コードではなく運用)
**確立済みの運用規約**: `/tmp` はマウント同期ラグがあるため、ツールの入出力は環境変数 **`WS_TMP`** で
作業フォルダ内を指す。入力JSONは bash heredoc で書く(スケジュール・プロジェクトプロンプトで規定)。
- `pending_char.py:8` は `os.environ.get("WS_TMP", "/tmp")` で**既に対応済**。`apply_char.py` のinboxは引数渡し。
- → **Windowsでは `WS_TMP=<project>\_ws_tmp` を設定**(`_ws_tmp/` フォルダは既存)。これで主経路の `/tmp` 問題は解消。
- RUNBOOKに残る `1>/tmp/pending.json` 等の素の `/tmp` リダイレクトは、Bashツール(git-bash)なら有効。
  WS_TMP配下へ寄せるとさらに安全。`pending_proofread.py` の `/tmp` 直書きは予備経路につき低優先。

### B-5. `python3` → `python`(呼び出し名) — ✅ 完了 2026-06-15(シム方式)
RUNBOOK・スケジュールは全て `python3 _tools/...`。今回のネイティブPythonは **`python.exe` のみ**
(`python3.exe` エイリアスは無効化済、git-bashにも `python3` は通常無い)。Windowsネイティブでは `python3` が解決不可。
**実施**: シム方式を採用。`%LOCALAPPDATA%\Programs\Python\Python312\python3.exe` を
`python.exe` のコピーで作成。`python3 --version` → `Python 3.12.10` を確認。
→ RUNBOOK・スケジュール・ドキュメントは無編集のまま `python3` が通る(Linux互換も温存)。

### B-7. `PYTHONIOENCODING=utf-8`(★実機検証で発覚) — 運用必須
Windowsの既定stdoutは cp932。`pending_char.py` 等が JSON/CJK を `print` する際、
一部文字(例 务务)で `UnicodeEncodeError` → crash(exit 1)。deployログも文字化け。
**対応**: 実行前に環境変数 `PYTHONIOENCODING=utf-8` を設定(スケジュール/RUNBOOK冒頭で1行)。
2026-06-15 司馬鈴の実走で確認: 設定すれば pending_char→apply_char→deploy が全段 exit 0・文字化けなし。
※恒久対応するなら各スクリプト先頭で `sys.stdout.reconfigure(encoding="utf-8")` でも可。当面は環境変数で運用。

### B-6. スケジュール実行環境の方針(要決定)
継続マシン(Sonnet)のスケジュールは現状 Linuxサンドボックス(`/sessions/<id>/mnt/...`)前提のプロンプト。
Windowsローカルへ移すなら、プロンプトのパス・`python3`・WS_TMP を上記に合わせて改訂が必要。
クラウド(Linux)のまま継続する選択肢もある。**移行範囲の決定事項**(本チャットでは保留)。

---

## C. ユーザー側の環境設定(GUI操作・1回だけ)

### C-1. Microsoft Store版 Python スタブの無効化(重要)
`where python` の先頭が今も `...\WindowsApps\python.exe`(Storeスタブ)。素の `python` がスタブに化ける。
- 設定 → アプリ → アプリの詳細設定 → **アプリ実行エイリアス** → **python.exe / python3.exe を両方オフ**。
- これで素の `python` が 3.12.10 を指す(新規シェルで有効)。
- 代替: PATHで `...\Programs\Python\Python312\` と `...\Python312\Scripts\` を WindowsApps より前に並べる。

### C-2. PATH反映
winget導入直後の現行シェルにはPATH未反映。**Claude Code / ターミナルを再起動**すれば反映。

---

## D. 移行後の検証手順(順に)

1. `python --version` → `Python 3.12.10`(スタブでないこと)
2. `python _tools/status.py` → 進捗が表示される(スタブだと無反応だった)
3. `_tools/repak.exe --version` → `repak_cli 0.2.3`
4. ドライラン: `python _tools/pending.py 1`(フェーズ判定が動くか)
5. 1サイクル実走: RUNBOOK フェーズ2の手順1〜5を200件で1回 → `apply_char.py` まで通り
   `_work/aaWanderingSword_JP_P.pak` が再生成されることを確認
6. `python _tools/deploy_to_game.py` → ゲームPaksへ差し替え＋日本語自己検証が通る
   (※ゲーム終了中に実行。起動中はスキップされる)

---

## 補足
- 失敗時は `_backup/aaWanderingSword_JP_P.original.pak` から復元可能。
- pak形式は `--version V11` 固定(repak 0.2.3 で対応)。
- 修正は B-1〜B-3 の3点が本体。B-1 だけでも校正サイクル(apply_char)は回る。deploy まで自動化するなら B-2/B-3 も。
