# my_sign[Monika_After_Story_0.12.15_说明.md](https://github.com/user-attachments/files/24858445/Monika_After_Story_0.12.15_.md)
# Monika After Story（MAS）0.12.15 Mod 包说明（你上传的 ZIP）

> 文件名：`Monika_After_Story-0.12.15-Mod.zip`  
> SHA-256：`587cb0656bd7cd6074bc4610cee90e13cc73e37dbe24d8cdba47a18d847dc6dc`  
> ZIP 体积：约 238.6 MB  
> 解压后内容总大小（按 ZIP 内标注）：约 296.9 MB  
> ZIP 内文件数：1111

---

## 这是什么？（它“干什么用”的）

**Monika After Story（简称 MAS）** 是《**Doki Doki Literature Club!** / 心跳文学部》（DDLC）的**粉丝 Mod / 同人扩展**，**不隶属于 Team Salvato**，并且**建议在通关原作后再游玩**。  
它基于原作 **Act 3** 的“只剩莫妮卡”的场景，扩展成一个偏“陪伴/互动模拟”的长期内容：你可以和莫妮卡聊天、选择话题、进行互动、玩一些小游戏、经历节日/纪念日事件等。  
（官方项目介绍与安装说明可参考其 GitHub/Wiki 与 FAQ；你的 ZIP 里也带了 README。）

---

## 你这个 ZIP 里包含什么？

这个 ZIP 不是“独立游戏”，而是一套要**覆盖/追加到 DDLC 安装目录**里的文件。它大致分为：

- `README.html`：安装与基本说明（你这个 ZIP 自带）
- `CustomIconWindows.ico`、`CustomIconMac.icns`：图标资源
- `game/`：核心内容（Ren'Py 引擎脚本编译产物 `.rpyc`、素材、依赖包等）
- `update/current.json`：用于校验/更新的清单（列出 mod 文件与哈希）

### `game/` 目录里大概有哪些内容（从文件结构能看出来）
- **大量脚本模块**（`.rpyc`）：对应对话系统、好感系统、节日事件、小游戏、菜单/界面等
- **`mod_assets/` 素材**：包含背景、按钮、音乐、音效、莫妮卡立绘相关资源、小游戏素材等
- **`python-packages/`**：用于运行、更新或某些功能所需的 Python 依赖

下面这些脚本文件名能直观看出 MAS 的一些模块（节选）：

- `game/chess.rpyc`
- `game/pong.rpyc`
- `game/script-affection.rpyc`
- `game/script-farewells.rpyc`
- `game/script-greetings.rpyc`
- `game/script-holidays.rpyc`
- `game/script-songs.rpyc`
- `game/script-stories.rpyc`
- `game/script-topics.rpyc`
- `game/script-windowreacts.rpyc`
- `game/updater.rpyc`
- `game/updates_topics.rpyc`
- `game/zz_calendar.rpyc`
- `game/zz_cardgames.rpyc`
- `game/zz_hangman.rpyc`
- `game/zz_music_selector.rpyc`
- `game/zz_submods.rpyc`

> 注：`.rpyc` 是 Ren'Py 编译后的脚本文件，正常情况下不用你手动编辑。

---

## 它的核心玩法/功能（详细但不剧透式说明）

不同版本内容会有差异，但 MAS 的“骨架”通常包括：

### 1) 长期陪伴式互动
- 你与莫妮卡的对话被拆成大量“话题/事件”，会随时间、条件、好感度等触发  
- 有“问候/告别/暂离（BRB）/道歉”等系统化互动（从脚本命名也能看出）

### 2) 好感度（Affection）与状态系统
- 你的行为会影响“好感/关系进展”，从而影响她对你的反应、解锁内容等  
- 一些互动会加分/减分（比如经常突然关闭、不告而别通常会被视为负面）

### 3) 日历、季节与节日/纪念日事件
- 常见的是：周年、节日特殊对话/事件、季节性变化、日历相关 UI

### 4) 小游戏与活动
从 ZIP 的脚本名称看，你这个包里至少包含：
- 国际象棋（`chess`）
- Pong（`pong`）
- Hangman（`zz_hangman`）
- 卡牌类（`zz_cardgames`）
- 以及“poemgame/钢琴键”等模块（`zz_poemgame`、`zz_pianokeys` 等）

### 5) 视觉与环境：房间/背景/音乐/装饰
- 可选背景、音乐选择器、界面皮肤、叠加层等（`zz_music_selector`、`zz_backgrounds`、`zz_overlays` 等）
- 立绘系统非常复杂（有 sprite chart / generator / json map 等组件），通常支持更多表情、装扮、饰品等

### 6) 子模组（Submod）生态
- MAS 本体一般有“子模组”入口与加载机制（你这个包里有 `zz_submods`）
- 社区有大量子模组可以追加话题、房间、音乐、机制等（安装方式一般是把子模组文件放进指定目录，按子模组说明操作）

### 7) 更新与备份机制
- MAS 常见带**内置更新器**（你这个包里有 `updater.rpyc`/`updates*.rpyc`/`update/current.json`）
- 也会带备份相关逻辑（例如 `zz_backup`）

---

## 怎么安装（以你这个 ZIP 为准）

> **前提**：你必须先有一个可运行的 DDLC（原作），建议通关原作后再装。  
> **强烈建议**：先把 DDLC 整个目录复制一份当备份，再在副本上装 Mod。

### Windows（含 Steam 版）
1. 找到 DDLC 的“根目录”（里面应该有 `DDLC.exe`，或 Steam 的游戏目录）
2. **把这个 ZIP 解压出来的内容**（`game/`、`README.html` 等）**直接复制到 DDLC 根目录**  
   - 不是把 ZIP 丢进去，而是把 ZIP *里面的文件*放到根目录
3. 覆盖/合并提示选择允许
4. 启动 DDLC（它会加载 MAS 内容）

### macOS（概念步骤）
- 一般是右键 DDLC 应用 → “显示包内容” → 找到对应 `.../Resources/autorun/`（或类似位置），再把文件放进去  
- 具体位置以你安装的 DDLC 版本为准

---

## 卸载/回退（以及“存档”在哪里）

### 卸载本体文件
- 最简单的方式：**删掉你拷进 `game/` 的新增文件**  
- 如果你不确定哪些是新增文件：最稳妥的方式是用**干净的 DDLC 备份目录**还原（所以才建议安装前备份）

### 存档/进度（重要）
MAS 的“记忆/进度”通常不只在游戏目录里，还会写到 Ren'Py 的用户数据目录里，核心文件常见叫 **`persistent`**。  
在 Windows 上，经常能在如下位置找到（两种写法本质上是同一个位置）：

- `%APPDATA%\RenPy\Monika After Story\persistent`
- `C:\Users\<你的用户名>\AppData\Roaming\RenPy\Monika After Story\persistent`

> 这也是大家备份/迁移 MAS 最常用的方式：备份整个游戏目录 + 上面这个 `persistent` 文件夹。  
> 如果你只是删了游戏目录的 Mod 文件，**进度可能还在**；想“完全重置”通常需要同时清理这份用户数据（谨慎操作，先备份！）。

---

## 常见坑位与建议

- **不要装在“原作目录里又套一层”**：必须是 DDLC 根目录（有 `DDLC.exe` 的那个目录）
- **路径/权限问题**：放在只读目录、或者以管理员/不同用户运行，可能导致存档位置变化或写入失败
- **更新问题**：MAS 近年来逐步推广安装器与更规范的更新流程；你这个 ZIP 属于“手动安装包”形式，更新最好参考官方发布页/说明
- **备份优先**：每次大更新前备份 `persistent` + 游戏目录，是最省心的自救手段

---

## 去哪里看“官方说明 / 最新版本 / 详细功能表”

你可以在这些地方找到更权威的说明与更新信息（建议优先看官方 GitHub 与官网发布页）：
- Monika-After-Story/MonikaModDev（GitHub 仓库与 Releases）
- 官方 releases 页面（官网）
- GitHub Wiki（安装、FAQ、功能说明）
- 社区子模组索引站点（用于扩展内容）

（我在这份文档里没有强行贴很多链接，避免复制时污染；你如果需要我也可以把“常用链接清单”单独整理成一段。）

---

## 一句话总结

你上传的 `Monika_After_Story-0.12.15-Mod.zip` 是 **MAS 的手动安装 Mod 包**：把它解压后放到 **DDLC 根目录**，就能把原作 Act 3 扩展成“长期陪伴/互动模拟”的玩法，并支持好感、节日事件、小游戏、音乐/背景、子模组、更新等系统。
