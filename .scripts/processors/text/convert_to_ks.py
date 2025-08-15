from __future__ import annotations
from pathlib import Path
from typing import List, Tuple

# 依存: python-docx
from docx import Document

# ===== KS 固定タグ（必要に応じて編集可） =====
TOP = "\n".join([
    "[mask  time=\"1000\"  effect=\"fadeIn\"  color=\"0x000000\"  ]",
    "[stopbgm  time=\"1500\"  fadeout=\"true\"  ]",
    "[tb_show_message_window  ]",
    "[bg  time=\"1000\"  method=\"crossfade\"  storage=\"room.jpg\"  ]",
    "[mask_off  time=\"1000\"  effect=\"fadeOut\"  ]",
]) + "\n\n"

END = "\n".join([
    "[chara_hide_all  time=\"1000\"  wait=\"true\"  ]",
    "[jump  storage=\"\"  target=\"\"  ]",
]) + "\n"

# ===== パラメータ =====
# 1行の想定最大文字数（全角/半角を等価とみなす簡易モデル）
N_MAX = 38
# 1ブロックで許容する本文行数
M_MAX = 3


# ---------- 入力読み込み ----------
def read_txt_lines(p: Path) -> List[str]:
    with p.open("r", encoding="utf-8") as f:
        return [ln.strip() for ln in f.readlines()]

def read_docx_lines(p: Path) -> List[str]:
    doc = Document(str(p))
    return [para.text.strip() for para in doc.paragraphs]


# ---------- 前処理（空行除去・話者/台詞の正規化・話者解除の # 挿入） ----------
def normalize_lines(raw_lines: List[str]) -> List[str]:
    # 1) 空行除去 & strip済み前提
    lines = [ln for ln in raw_lines if ln]

    # 2) 「行頭が '名前「...'」の行」を「#名前」「「...」」の二行に分離
    import re
    norm: List[str] = []
    pat = re.compile(r'^(.+?)「(.*)')
    for ln in lines:
        m = pat.match(ln)
        if m:
            speaker, rest = m.group(1), m.group(2)  # rest は 「 以降
            if not speaker.startswith("#"):
                norm.append(f"#{speaker}")
            else:
                norm.append(speaker)
            norm.append("「" + rest)
        else:
            norm.append(ln)

    # 3) 台詞が '」' で終わり、次行が '「' で始まらないなら、次に '#'（話者解除）を挿入
    out: List[str] = []
    for i, ln in enumerate(norm):
        out.append(ln)
        if ln.endswith("」"):
            nxt = norm[i + 1] if i + 1 < len(norm) else ""
            if not nxt.startswith("「"):
                out.append("#")  # 話者解除（地の文へ）
    return out


# ---------- ブロック分割（# を境界とする） ----------
def split_blocks(lines: List[str]) -> List[Tuple[str|None, List[str]]]:
    """
    返り値: [(header_line_or_None, body_lines), ...]
    header_line は '#...' or '#'、先頭が地の文だけなら header=None
    """
    blocks: List[Tuple[str|None, List[str]]] = []
    header: str|None = None
    body: List[str] = []

    def flush():
        nonlocal header, body, blocks
        if header is None and not body:
            return
        blocks.append((header, body))
        header, body = None, []

    for ln in lines:
        if ln.startswith("#"):
            # 次のブロックを開始
            flush()
            header = ln  # '#...' or '#'
        else:
            body.append(ln)

    flush()
    return blocks


# ---------- 本文のサブブロック化（行数 M_MAX / 総文字 N_MAX*M_MAX 制約） ----------
def split_body_greedily(body: List[str], n_max: int, m_max: int) -> List[List[str]]:
    subs: List[List[str]] = []
    cur: List[str] = []
    cur_chars = 0
    limit_chars = n_max * m_max

    i = 0
    while i < len(body):
        line = body[i]
        L = len(line)

        # 先頭（cur 空）で行が長すぎる → 句点優先で切る（なければ強制折り）
        if L > limit_chars and not cur:
            segments = split_line_by_punctuation(line, limit_chars)
            for seg in segments[:-1]:
                subs.append([seg])  # 1行完結のサブブロックとして確定
            # 末尾の残りをこの後の通常処理に回す
            line = segments[-1]
            L = len(line)

        # 次の行を追加したら制約超え？
        if (len(cur) + 1) > m_max or (cur_chars + L) > limit_chars:
            if cur:
                subs.append(cur)
                cur, cur_chars = [], 0
                # ← 同じ行を「先頭行」として再評価するため continue
                continue
            else:
                # cur が空なのに入らないケース（極端な長文）→ 保険
                subs.append([line[:limit_chars]])
                body[i] = line[limit_chars:]
                continue

        # 追加して継続
        cur.append(line)
        cur_chars += L
        i += 1

    if cur:
        subs.append(cur)
    return subs


def split_line_by_punctuation(s: str, limit: int) -> List[str]:
    """一行が長すぎる場合、'。' を優先して limit 以内で右から切る。無ければ強制折り。"""
    res: List[str] = []
    cur = s
    while len(cur) > limit:
        cut = cur.rfind("。", 0, limit)
        if cut == -1:
            # 句点がない → 強制折り
            res.append(cur[:limit])
            cur = cur[limit:]
        else:
            res.append(cur[:cut+1])
            cur = cur[cut+1:]
    if cur:
        res.append(cur)
    return res


# ---------- KS 文字列生成 ----------
def render_ks(blocks: List[Tuple[str|None, List[str]]]) -> str:
    parts: List[str] = []

    for header, body in blocks:
        # 本文をサブブロック化
        subblocks = split_body_greedily(body, N_MAX, M_MAX)

        for sub in subblocks:
            parts.append("[tb_start_text mode=3 ]")
            if header is not None:
                parts.append(header)  # '#...' or '#'

            # 本文行の [l][r]/[p][r] 付与
            if sub:
                for ln in sub[:-1]:
                    parts.append(f"{ln}[l][r]")
                parts.append(f"{sub[-1]}[p][r]")

            parts.append("[_tb_end_text]")
            parts.append("")  # 空行

    return "\n".join(parts).rstrip() + "\n"


# ---------- パイプライン・ステップ ----------
def convert_to_ks(in_path: Path, dst_dir: Path, base_name: str) -> bool:
    """
    .txt / .docx をティラノ .ks へ変換するステップ。
    - 対象拡張子でなければ False を返し、後続（最終的にはコピー）に委ねる。
    """
    ext = in_path.suffix.lower()
    if ext not in {".txt", ".docx"}:
        return False

    # 入力 → 行列化
    if ext == ".txt":
        raw = read_txt_lines(in_path)
    else:
        raw = read_docx_lines(in_path)

    # 正規化・分割
    lines = normalize_lines(raw)
    blocks = split_blocks(lines)
    ks_text = (
        f"[_tb_system_call storage=system/_{Path(base_name).stem}.ks]\n"
        + TOP
        + render_ks(blocks)
        + END
    )
    out_path = dst_dir / Path(base_name).with_suffix(".ks").name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(ks_text, encoding="utf-8")

    print(f"[TEXT->KS] {in_path.name} -> {out_path.relative_to(dst_dir)}")
    return True



"""
.  docxファイルもtxt同様に読み込む
1. まず元ファイルの空行をすべて消す。
2. そこから元ファイルのテキストの行ごとに処理を行う。
3. まずstrip()
4. 行頭の処理
    - '(.+?)「'で始まる行は先頭に '#' を付ける。
    - '」'で終わり、次の行が '「' で始まらない場合は次の行に新規行として '#' のみの行を追加する。

5. ブロック化
    - まず最初の#を見つける。
    - 最初の行から最初の#の直前行までを1つのブロックとして扱う。
    - その#から次の#の前の直前行までを1つのブロックとして扱う。
    - 各ブロックを更に分割する。
    - まず、1行分の文字数(N)と1つのブロックの最大行(M)を決めておく。
    - 各ブロックの先頭行の文字数を数える。それがN x M文字を超える場合は文中の句点("。")で分割
    - 超えてなければ先頭行に次の行を足した文字数を数える（ただしこの場合最初の行をM文字として数えるように修正）。
        - その合計文字数がN x M文字を超える場合はそれぞれは別ブロックとし、次の行について同様の処理を続ける。
        - その合計文字数がN x M文字を超えない場合は次の行を足していく。
    - このようにして各ブロックを「N行以下、かつ、N x M文字以下」の形に更に分割していく。

5. 行末の処理
    - '#' のみの行はそのまま
    - 各ブロックの最後の行は[p][r]を付ける。
    - それ以外の行は[l][r]を付ける。
    
6. ティラノスクリプトの形式に変換
    - "(.+?)「(.*?)"で始まる行（"#アキラ「来週のLHRまでに脚本の草案を仕上げて..."のような行）は
    "#アキラ
    「来週のLHRまでに脚本の草案を仕上げて..."
    のように"「"の前で開業するように変換する。
    - 各ブロックの前の行に新規行として[tb_start_text mode=3 ]を付ける。
    - 各ブロックの後の行に新規行として[_tb_end_text]を付ける。
    - 全体の最初の行にtopを付ける。
    - 全体の最後の行にendを付ける。


注意事項
・なぜ"#" を付けるのか？
    - ティラノスクリプトの仕様で、行頭に「#xxx」があるとその行は発言者(xxx)の名前を表すシステムテキストとして認識される。これはテキスト欄の文字数に含まれないのでこのような処理になっている。
    - "#"のみの行があるのは、以降が地の文となるため、特定の発言者を指す必要がないから、システムテキストを空白にするため。
・ 既存ファイルとの比較はgithub側が勝手にやってくれるので、特に意識しなくてよい。よってks_text_equal()周辺の処理は省いてよいはず
・ 今回は各ファイルごとに処理を適用するので、sortedやfilesに対するfor文は不要なはず
・ ファイル名は末尾を.ksに変えるだけで良い
"""