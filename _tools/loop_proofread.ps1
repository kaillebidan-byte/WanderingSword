# フェーズ2校正の自動ループ(headless Sonnet)。
# 1バッチ=1新プロセス(文脈肥大なし)。char_progressで再開可。
# 未確定/保留に当たる or 進捗停滞で自動停止。トークン枯渇は sleep して再開。
# 使い方: powershell -ExecutionPolicy Bypass -File _tools\loop_proofread.ps1 [-Max 500] [-SleepOnLimit 1800]
param(
  [int]$Max = 500,          # 最大イテレーション(暴走止め)
  [int]$SleepOnLimit = 1800 # トークン枯渇時の待機秒(既定30分)
)
$ErrorActionPreference = "Continue"
$proj = "C:\Users\kaill\Claude\Projects\Wandering Sword翻訳"
Set-Location $proj
# 子プロセスはSet-Locationではなく[Environment]::CurrentDirectoryをcwdとして継承する。揃えておく。
[Environment]::CurrentDirectory = $proj
$env:WS_TMP = "$proj\_ws_tmp"
$env:PYTHONIOENCODING = "utf-8"
# claude.exeを直接Start-Processで起動(cmd不要・クォート無し)。stdin/stdoutはファイルでやり取り。
# パスは絶対指定。$env:APPDATAは管理者/別コンテキストのPowerShellで別プロファイルを指し、
# claude実体が見つからなくなる(=過去の「claude.cmd未認識」の真因)。$projと同様にハードコードする。
$claudeExe = "C:\Users\kaill\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe"
$P4 = "$proj\_phase4_proofread"
$log = "$env:WS_TMP\loop_proofread.log"
$promptFile = "$env:WS_TMP\loop_prompt.txt"   # 校正指示(UTF-8)。stdinから投入=CJK化け回避
$outF = "$env:WS_TMP\claude_out.txt"           # claude標準出力
$errF = "$env:WS_TMP\claude_err.txt"           # claude標準エラー

function Get-Prog { try { Get-Content "$P4\char_progress.json" -Raw | ConvertFrom-Json } catch { $null } }
# PS5.1のConvertFrom-Jsonは2.9MBの全オブジェクトグラフ展開で事実上ハングする。
# 必要なのはorder(888要素)だけなので、pythonでorderだけ抜き出しUTF-8で書き出す(CJK保持)。
$orderFile = "$env:WS_TMP\by_character_order.json"
& python -c "import json; d=json.load(open(r'$P4\by_character.json',encoding='utf-8')); json.dump(d['order'], open(r'$orderFile','w',encoding='utf-8'), ensure_ascii=False)"
$order = Get-Content $orderFile -Raw -Encoding UTF8 | ConvertFrom-Json
$total = $order.Count
function Log($m) { $ts = Get-Date -Format "HH:mm:ss"; "$ts $m" | Tee-Object -FilePath $log -Append }

Log "=== loop開始 total=$total ==="
$stall = 0
for ($i = 1; $i -le $Max; $i++) {
  $p = Get-Prog
  if ($null -eq $p -or $p.ci -ge $total) { Log "全キャラ完了(ci=$($p.ci)/$total)。終了。"; break }
  $cur = $order[$p.ci]
  Log "[$i] 開始 ci=$($p.ci) pos=$($p.pos) キャラ=$cur"

  # 1バッチ実行(headless sonnet・許可スキップ・プロンプトはUTF-8ファイルからstdin投入)
  # claude.exeを直接起動。stdinはpromptFile(生バイト=UTF-8保持)、出力はファイル経由でUTF-8読み戻し。
  $proc = Start-Process -FilePath $claudeExe `
    -ArgumentList '-p', '--model', 'sonnet', '--dangerously-skip-permissions' `
    -RedirectStandardInput $promptFile -RedirectStandardOutput $outF -RedirectStandardError $errF `
    -WorkingDirectory $proj -NoNewWindow -Wait -PassThru
  $sout = (Get-Content $outF -Raw -Encoding UTF8); $serr = (Get-Content $errF -Raw -Encoding UTF8)
  $text = "$sout`n$serr"
  $text | Out-File -FilePath $log -Append -Encoding utf8

  # 結果判定
  if ($text -match "未確定|保留|status:\s*確定 でない") {
    Log "→ 未確定/保留に到達($cur)。Opus介入が必要。停止。"; break
  }
  if ($text -match "(?i)session limit|usage limit|rate limit|quota|too many requests|hit your (session|usage)|resets?\s+\d|利用上限|上限") {
    # 「resets 7:40am」等を拾えればその時刻まで、無ければ既定秒。
    $wait = $SleepOnLimit
    if ($text -match "(?i)resets?\s+(\d{1,2}):(\d{2})\s*(am|pm)?") {
      $h = [int]$Matches[1]; $m = [int]$Matches[2]; $ap = $Matches[3]
      if ($ap -eq "pm" -and $h -lt 12) { $h += 12 }
      if ($ap -eq "am" -and $h -eq 12) { $h = 0 }
      $now = Get-Date; $target = Get-Date -Hour $h -Minute $m -Second 0
      if ($target -le $now) { $target = $target.AddDays(1) }
      $wait = [int](($target - $now).TotalSeconds) + 120
    }
    Log "→ セッション/トークン上限に到達。$([int]($wait/60))分待機してリセット後に再試行。"
    Start-Sleep -Seconds $wait; continue
  }

  # 進捗が進んだか(停滞検知)
  $p2 = Get-Prog
  if ($p2.ci -eq $p.ci -and $p2.pos -eq $p.pos) {
    $stall++
    Log "→ 進捗が動かず(stall=$stall)。応答末尾: $($text.Substring([Math]::Max(0,$text.Length-200)))"
    if ($stall -ge 2) { Log "→ 2回連続で停滞。異常とみて停止。" ; break }
  } else {
    $stall = 0; Log "→ 前進 ci=$($p2.ci) pos=$($p2.pos)"
  }
  Start-Sleep -Seconds 3
}
Log "=== loop終了 ==="
