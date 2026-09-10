# LabSpec6 L6S to TXT · 拉曼光谱批量转换

A lightweight, standard-library-only Python converter for **HORIBA LabSpec6 `.l6s` single Raman spectra → tab-separated TXT**, with basic metadata sidecars. No RamanLab, NumPy, SciPy or Qt installation required.

轻量级 **HORIBA LabSpec6 `.l6s` 单条拉曼光谱 → TXT 批量转换工具**。仅依赖 Python 标准库，支持 Windows 拖入、多选文件、文件夹和命令行；不启动光谱分析软件。

**[Usage & configuration / 使用与配置（中英双语）](USAGE_CONFIGURATION.md)**

## Quick start / 快速开始

1. Download this repository with **Code → Download ZIP**, then extract it. / 点击 **Code → Download ZIP** 下载并解压。
2. Use **Python 3.9+**. The Windows file picker also needs Python's bundled Tcl/Tk. / 安装 **Python 3.9+**，Windows 选择窗口需要自带的 Tcl/Tk。
3. On Windows, double-click **`Convert_L6S.bat`** to select multiple files, or drag files/folders onto it. Double-click **`Select_Folder.bat`** to choose a folder. / 双击前者多选文件，或拖入文件/文件夹；双击后者选择文件夹。

```shell
python -X utf8 l6s_to_txt.py "path/to/sample.l6s"
python -X utf8 l6s_to_txt.py "path/to/data" --recursive -o "path/to/output"
```

On macOS/Linux, use `python3` if needed. Windows is the locally tested platform; other platforms have not been verified. / macOS/Linux 可按环境改用 `python3`；目前实测平台为 Windows，其他平台尚未验证。

## Outputs / 输出

By default, each source directory gets a `txt_export` subdirectory. / 默认在各源目录内建立 `txt_export`。

| File / 文件 | Contents / 内容 |
|---|---|
| `sample.txt` | Raman shift (cm⁻¹), intensity; Tab-separated, one commented header / 波数与强度两列，Tab 分隔，首行为注释表头 |
| `sample.metadata.txt` | Decoded sample name, source path, SHA256, point count, ranges and conversion time / 已解出的样本名、源路径、校验值、点数、范围和转换时间 |

Existing outputs receive numeric suffixes; input files are never edited. Failed files do not stop the batch. No baseline correction, smoothing, normalization or peak fitting is performed. / 重名自动编号，原文件不修改，单个失败不终止批次；不扣背景、不平滑、不归一化、不拟合。

## Scope and validation / 支持范围与验证

- Supports the single-spectrum block layouts recognized by this parser, **not every LabSpec6 version or `.l6m` maps**. / 仅支持解析器已识别的单谱布局，**不保证所有 LabSpec6 版本，不支持 `.l6m` mapping**。
- Axis recognition requires 50+ increasing points, 40–5000 cm⁻¹ and steps of 0.3–20 cm⁻¹ (bounds exclusive). Unsupported layouts fail explicitly. / 波数轴需至少 50 点、递增、范围与步长满足上述严格边界；未知布局报错。
- **Basic metadata only**: laser wavelength, laser power, exposure, accumulations and acquisition timestamp are not decoded. / **仅基础元数据**：尚未解出激光波长、功率、曝光、积分次数和采集日期。
- Tested locally on one 1103-point real spectrum against the patched RamanLab reader; all decoded values and float32 TXT round trips matched. Synthetic regression tests cover both supported layouts and failure cases. The real spectrum is not distributed. / 已用一份 1103 点真实光谱与修复后的 RamanLab 核对；数值及 float32 TXT 往返一致。附合成回归测试，不发布实验样本。
- **Not yet validated against an official LabSpec6 TXT export.** Perform that comparison before quantitative use. / **尚未与 LabSpec6 官方 TXT 导出逐点对照**，定量使用前请完成该验证。

## Dependencies and size / 依赖与体积

No third-party Python packages: no `pip install` step. The converter itself is approximately 9 KB; documentation and tests add a small amount. This is a script distribution, **not a standalone EXE**, and does not bundle Python. / 无第三方 Python 包，无需 `pip install`。核心脚本约 9 KB，文档和测试另占少量空间；本项目是脚本发行版，**不是独立 EXE**，不含 Python。

```shell
python -S -X utf8 -m unittest test_converter -v
```

## Acknowledgements / 致谢

Thank you to **Aaron Celestian and the [RamanLab](https://github.com/aaroncelestian/RamanLab) project** for making their Raman spectroscopy software open source. This converter was built on RamanLab's LabSpec6 binary-format parsing work, especially `utils/labspec6_parser.py`. That open-source foundation made this lightweight data-conversion tool possible.

感谢 **Aaron Celestian 及 [RamanLab 开源项目](https://github.com/aaroncelestian/RamanLab)** 公开分享拉曼光谱分析软件及 LabSpec6 数据解析实现。本工具基于 RamanLab 的二进制格式解析工作，尤其是 `utils/labspec6_parser.py`，实现轻量化数据转换、批量处理与 TXT 导出。感谢原项目为本工具提供的开源基础。

## License and attribution / 许可与来源

MIT; see [LICENSE](LICENSE). Binary layout knowledge and parsing logic were adapted from [RamanLab](https://github.com/aaroncelestian/RamanLab), specifically `utils/labspec6_parser.py`, with a standard-library rewrite, stricter boundary checks and batch export support. The upstream copyright notice is retained. / 采用 MIT 许可；二进制结构与解析逻辑源自 RamanLab，改写为标准库实现，并增加边界验证和批量导出，保留上游版权声明。

This is an independent community utility, not an official HORIBA product. / 本项目为独立社区工具，非 HORIBA 官方产品。
