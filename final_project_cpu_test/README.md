# final_project_cpu_test

用于在**本地 CPU**上做小规模冒烟测试，快速验证项目链路是否可运行。

## 作用

- 强制使用 `MODEL_DEVICE=cpu`
- 从 `coco-wholebody` 抽样少量图片（默认 `val2017` 的 5 张）
- `auto/full/lite` 三种模式（`auto` 默认，失败自动降级）
- 输出可视化图片和 `summary.json` 报告

## 运行前准备

推荐直接使用下方的一键脚本（默认安装轻量依赖），避免本地 Windows 编译 `mmcv` 失败。

## 快速开始

```bash
cd /path/to/final_project
python final_project_cpu_test/run_cpu_smoke_test.py
```

Windows PowerShell 示例：

```powershell
cd d:\final_project
python .\final_project_cpu_test\run_cpu_smoke_test.py --samples 3
```

## Windows 一键安装并测试

```powershell
cd d:\final_project
powershell -ExecutionPolicy Bypass -File .\final_project_cpu_test\setup_local_cpu_env.ps1 -Samples 3 -Split val2017
```

常用参数：

- `-ProjectRoot`：项目根目录（默认自动识别）
- `-PythonExe`：Python 命令（默认 `python`）
- `-Samples`：抽样数（默认 `3`）
- `-Split`：`train2017` / `val2017`
- `-InstallProfile`：`lite`（默认，仅轻量依赖）/`full`（安装 backend 全依赖）
- `-TestMode`：`auto`（默认）/`full`（强制真实推理）/`lite`（仅链路检查）
- `-SkipInstall`：跳过依赖安装（已装好依赖时更快）

## 常用参数

- `--data-root`：数据集根目录（默认 `<project-root>/coco-wholebody`）
- `--split`：`train2017` 或 `val2017`（默认 `val2017`）
- `--samples`：抽样数量（默认 `5`）
- `--model-name`：覆盖模型名（默认使用 Django settings 中的 `MODEL_NAME`）
- `--mode`：`auto/full/lite`
- `--output-dir`：输出目录（默认 `final_project_cpu_test/outputs`）

示例：

```bash
python final_project_cpu_test/run_cpu_smoke_test.py \
  --data-root d:/final_project/coco-wholebody \
  --split val2017 \
  --samples 5 \
  --output-dir d:/final_project/final_project_cpu_test/outputs
```

## 输出说明

- `outputs/*_vis.jpg`：关键点可视化结果
- `outputs/summary.json`：测试报告（成功/失败数量、模式、报错信息）

