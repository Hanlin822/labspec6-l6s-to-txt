# Usage & Configuration · 使用与配置说明

## 1. Requirements / 环境要求

| Component / 组件 | Requirement / 要求 |
|---|---|
| Python | 3.9 or newer / 3.9 及以上 |
| CLI conversion / 命令行转换 | Python standard library only / 仅 Python 标准库 |
| File/folder picker / 文件选择窗口 | `tkinter` + Tcl/Tk, included with a full Windows Python installation / 完整 Windows Python 安装通常自带 |
| Drag onto BAT / 拖到启动器 | Windows, `py` launcher or `python` on PATH / Windows，具有 `py` 启动器或 PATH 中的 `python` |
| Third-party packages / 第三方包 | None / 无 |

The scripts are independent of RamanLab and its virtual environment. Copy the tool folder anywhere you can read it. Do not move only the BAT files: keep them beside `l6s_to_txt.py`. / 脚本独立于 RamanLab 及其虚拟环境，可复制整个工具目录；不要仅移动 BAT，它们必须与 Python 脚本放在一起。

Check the interpreter / 检查解释器：

```powershell
py -3 --version
py -3 -c "import tkinter; print(tkinter.TkVersion)"
```

If `py` is unavailable, use `python`. There is no requirements file because no third-party installation is needed. / 无 `py` 时改用 `python`；无需第三方依赖，因此不需要 requirements 文件。

## 2. Windows quick workflow / Windows 快速流程

### A. Drag and convert / 拖入转换

Select one or more `.l6s` files and drop them onto **`Convert_L6S.bat`**. Folders are also accepted. Conversion runs immediately; the console lists results and pauses at the end. / 选择一个或多个 `.l6s` 文件，拖到 **`Convert_L6S.bat`** 图标上，也可拖入文件夹；立即转换，控制台逐项显示结果，结束后暂停。

For very large batches, pass a folder instead of dragging hundreds of paths; Windows has a command-line length limit. / 大批量请传文件夹，避免拖入数百个路径触及 Windows 命令行长度上限。

### B. Select multiple files / 多选文件

Double-click **`Convert_L6S.bat`**, use Ctrl/Shift in the file picker, then click Open. Cancel performs no conversion. / 双击 **`Convert_L6S.bat`**，用 Ctrl/Shift 多选，点击打开后自动转换；取消则不转换。

### C. Select a folder / 选择文件夹

Double-click **`Select_Folder.bat`**. By default, only `.l6s` files directly inside the selected folder are included. / 双击 **`Select_Folder.bat`**，默认只转换选中目录第一层的 `.l6s`。

To include subfolders / 包含子文件夹：

```powershell
.\Select_Folder.bat --recursive
```

The picker interface currently uses Chinese labels; the CLI options and per-file status lines are in English. / 当前选择窗口提示为中文，命令行选项及逐文件状态为英文。

## 3. Command line configuration / 命令行配置

No configuration file is needed. Options apply to the current run. / 无需配置文件，各选项只对本次运行生效。

| Option / 参数 | Meaning / 含义 | Default / 默认 |
|---|---|---|
| `paths` | One or more files/folders / 一个或多个文件或文件夹 | Open file picker / 打开文件选择框 |
| `-o`, `--output` | Shared output directory / 统一输出目录 | Each source directory's `txt_export` / 各源目录下的 `txt_export` |
| `-r`, `--recursive` | Include nested folders / 扫描子目录 | Off / 关闭 |
| `--pick-files` | Open multi-file picker / 打开多文件选择框 | Off / 关闭 |
| `--pick-folder` | Open folder picker / 打开文件夹选择框 | Off / 关闭 |
| `-h`, `--help` | Show help / 显示帮助 | — |

Run from the extracted tool directory. Quote paths containing spaces. / 在解压后的工具目录执行，含空格的路径加引号。

```powershell
# One file / 单文件
python -X utf8 l6s_to_txt.py "D:\Raman Data\sample.l6s"

# Multiple files / 多文件
python -X utf8 l6s_to_txt.py "D:\Raman Data\a.l6s" "D:\Raman Data\b.l6s"

# Folder, recursive, separate destination / 文件夹递归扫描并统一输出
python -X utf8 l6s_to_txt.py "D:\Raman Data" -r -o "D:\Raman TXT"

# File picker with a chosen output path / 弹窗选文件并指定输出目录
python -X utf8 l6s_to_txt.py --pick-files -o "D:\Raman TXT"

# Save a run log in PowerShell / PowerShell 保存运行日志
python -X utf8 l6s_to_txt.py "D:\Raman Data" 2>&1 | Tee-Object -FilePath conversion.log
```

The Python program returns 0 on success/cancellation, 1 for file/path failures, and 2 for usage/picker errors. For automation, call Python directly, rather than the interactive BAT wrapper. / Python 程序返回码：0 成功或取消，1 文件/路径失败，2 参数或选择窗口错误；自动化请直接调用 Python，不使用交互 BAT。

## 4. Output format / 输出格式

Each successful input creates a pair / 每个成功输入生成一对文件：

```text
txt_export/
  sample.txt
  sample.metadata.txt
```

The main TXT has one commented header and two Tab-separated columns. Scientific notation is valid. Values use nine significant digits to preserve decoded float32 round trips. / 主 TXT 有一行注释表头、两列 Tab 分隔数值；科学计数法正常；九位有效数字用于保留已解出 float32 的往返精度。

| Column / 列 | Value / 含义 |
|---|---|
| 1 | Raman shift, cm⁻¹ / 拉曼位移 |
| 2 | Decoded stored intensity; no processing / 文件中解出的强度，未加工 |

No baseline correction, smoothing or peak fitting occurs. A successful 1103-point conversion has 1103 data lines plus one header line. / 不扣背景、不平滑、不拟合；1103 点文件成功转换后是 1103 行数值加 1 行表头。

If a target name exists, `_001`, `_002`, etc. are added; existing files are not overwritten. Inputs with the same basename from different directories remain separate through this numbering when using `-o`. / 同名自动增加编号；使用统一输出目录时，不同源目录的同名文件也会编号保存。

## 5. Metadata scope / 元数据范围

The sidecar contains the decoded sample name when available, source path/size/SHA256, point count, axis and intensity ranges, mean axis step, negative-value count, converter information and conversion timestamp. / 附属 TXT 包含可解出的样本名、源路径/大小/SHA256、点数、波数与强度范围、平均步长、负值数量、转换器信息和转换时间。

**Conversion time is not acquisition time.** Laser wavelength/power, exposure, accumulation count and acquisition timestamp are not decoded. Retain original L6S files for complete experimental provenance. / **转换时间不是采集时间。** 激光波长/功率、曝光、积分次数和采集时间尚未解出；完整实验信息应保留原 L6S。

The sidecar records your local source path. Review it before sharing exports publicly. / 附属文件记录本地源路径，公开分享导出结果前可先检查这一字段。

## 6. Compatibility and validation / 兼容性与验证

- Single-spectrum `.l6s` only; no `.l6m` mapping or universal version support. / 仅单谱 `.l6s`，不支持 mapping，也不保证全部版本。
- Requires a recognized `1/cm` axis label, at least 50 increasing points, `40 < shift < 5000`, and `0.3 < step < 20`. / 需识别 `1/cm` 标签及满足上述范围、步长和点数。
- Both the axis and intensity payload must end at recognized block boundaries; ambiguous or incomplete layouts are rejected. / 波数轴与强度数组均需匹配块边界，歧义或不完整布局拒绝转换。
- One real spectrum matched the patched RamanLab reader, including float32 TXT round-trip comparison. This is limited evidence, not a general format certification. / 一份真实样本通过 RamanLab 数值及 TXT 往返对照，不能外推为所有格式均兼容。
- Official LabSpec6 TXT comparison is still required before quantitative use. / 定量使用前仍需 LabSpec6 官方 TXT 对照。

Run included synthetic tests without third-party packages / 不加载第三方包运行合成测试：

```powershell
python -S -X utf8 -m unittest test_converter -v
```

## 7. Troubleshooting / 故障处理

| Symptom / 现象 | Action / 处理 |
|---|---|
| Python not found / 找不到 Python | Install Python or fix PATH; try `py -3` / 安装 Python 或修正 PATH，尝试 `py -3` |
| Picker unavailable / 选择框无法打开 | Enable Tcl/Tk in Python installation, or pass paths via CLI / 安装 Tcl/Tk 组件，或直接传命令行路径 |
| Permission denied / 无写入权限 | Use `-o` with a writable destination / 用 `-o` 指定可写目录 |
| No `.l6s` files found / 没找到文件 | Check folder and extension; use `-r` for nested files / 检查目录与扩展名，子目录使用 `-r` |
| Unsupported axis/block / 波数轴或数据块不支持 | Keep original and full error; export TXT in LabSpec6 as fallback / 保留原文件与报错，可先从 LabSpec6 导出 TXT |
| Garbled console text / 控制台乱码 | Use supplied BAT or Python `-X utf8` / 使用启动器或加 `-X utf8` |

Do not rename other binary formats to `.l6s` to force conversion. / 不要通过改后缀强行转换其他二进制格式。

## 8. Distribution / 分发

This repository contains scripts and documentation, not Python or a standalone executable. No package installation is required when Python is already available. A future EXE would need to bundle the interpreter and possibly Tcl/Tk, so its size would be larger and must be measured separately. / 本仓库只含脚本和文档，不含 Python 或独立 EXE；已有 Python 无需装包，未来 EXE 需打包运行时，体积需另行实测。

MIT license; the upstream RamanLab copyright notice is retained in [LICENSE](LICENSE). / MIT 许可，保留 RamanLab 上游版权声明。
