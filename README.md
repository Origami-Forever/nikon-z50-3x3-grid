# 尼康 Z50 一代 3×3 取景网格

[English](README.en.md) | 简体中文

> \[!CAUTION]
> **刷机有风险，可能导致相机无法开机、无响应、设置丢失或失去保修。**
> 本项目不是 Nikon 官方软件，无法保证修改固件之后相机不会变砖。如果你不接受可能的风险，请不要刷机。
> 更新中断、错误型号或错误固件版本都可能造成不可恢复的故障。

本项目有两种使用方式：[方式一：直接下载](#方式一直接下载)，或 [方式二：手动构建](#方式二手动构建)，任选其一。

这是一个针对 **尼康 Z50 一代** C 2.60 的固件研究工具。它通过数据级补丁，把`d8 取景网格显示` 的网格线数量从 4×4 改为 3×3，不修改菜单，风险较小。

## 方式一：直接下载

请从以下 Release 下载：



* [GitHub Release](https://github.com/Origami-Forever/nikon-z50-grid/releases/tag/v0.1.0-z50-c260-3x3)

* [直接下载 ](https://github.com/Origami-Forever/nikon-z50-grid/releases/download/v0.1.0-z50-c260-3x3/EG163060.BIN)[EG163060.BIN](https://github.com/Origami-Forever/nikon-z50-grid/releases/download/v0.1.0-z50-c260-3x3/EG163060.BIN)

文件信息：



* 适用相机：**Nikon Z50 一代**

* 必需固件：C 2.60

* 大小：31,404,090 字节

* SHA-256：

  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`

使用步骤：



1. 确认 `设置菜单 -> 固件版本` 显示 **C 2.60**；

2. 核对下载文件的大小和 SHA-256；

3. 把 `EG163060.BIN` 放在相机格式化过的存储卡根目录；

4. 充满电池，关闭相机，插入存储卡；

5. 打开相机，按 `设置菜单 -> 固件版本` 的提示升级；

6. 更新完成前不要按键、拔卡或断电。

## 功能



* 保留原厂 `d8 取景网格显示` 开关；

* 开启网格时显示 3×3；

* 关闭网格时恢复原厂关闭行为；

* 只修改 6 个网格模板计数和模块 CRC；

* 不修改代码、跳转、指针、字体、菜单或传感器路径。

## 源码与固件边界

源码仓库不包含以下内容：



* 尼康官方固件；

* 解码后的固件模块；

* 旧版 XOR 密钥表。

已验证的修改后 EG 模块通过 GitHub Release 单独发布，不作为源码提交。

你需要自行取得未经修改的官方固件包：



| 相机               | 固件     | 文件              | 大小         | SHA-256                                                            |
| ---------------- | ------ | --------------- | ---------- | ------------------------------------------------------------------ |
| **Nikon Z50 一代** | C 2.60 | `Z_50_0260.bin` | 31,972,272 | `69745c9e8f3156e936918e62a4a1fad18e7078e9ea3b95d8b8e08144b1542e49` |

官方更新包使用尼康旧版 XOR 格式。构建工具会在本地解码并检查模块与包的

CRC，但不会下载固件，也不会连接或刷写相机。

768 字节旧版 XOR 表属于固件派生材料，因此不在仓库中提供。请自行取得合法

可用的本地副本，放在：



```
firmware/legacy_nikon_mask.hex
```

构建工具也接受 WonderLantern `nikon-fw-key-tool` 生成的 JSON 密钥文件。

## 方式二：手动构建

要求 Python 3.10 或更高版本。仅构建数据版 3×3 时可完全不使用第三方

Python 包。



```
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/build_grid3x3.py `
  --source firmware/Z_50_0260.bin `
  --output-dir output/grid3x3-v3
```

构建器不会覆盖已有文件。成功后会生成：



```
EG163060.BIN
grid3x3-report.json
```

已知已实机安装的构建为：



* 文件名：`EG163060.BIN`

* 大小：31,404,090 字节

* SHA-256：

  `241afae261d39633c7b7061a38719423980feacaf3a428996971b75fbf0ab2a1`

## 独立验证



```
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
python tools/verify_candidate.py `
  --source firmware/Z_50_0260.bin `
  --mask firmware/legacy_nikon_mask.hex `
  --candidate output/grid3x3-v3/EG163060.BIN
```

审计器会从官方包独立重建结果，并拒绝以下文件：



* 与独立重建结果不一致；

* 大小异常；

* 缺少预期修改；

* 存在未预期修改；

* 模块 CRC 残留不为零。

该构建只改变以下 6 个数据字段和末尾 2 字节 CRC：



| 运行地址         | 原厂值       | 3×3     |
| ------------ | --------- | ------- |
| `0x106627C2` | X `03 00` | `02 00` |
| `0x106627CE` | Y `03 00` | `02 00` |
| `0x106627E2` | X `03 00` | `02 00` |
| `0x106627EE` | Y `03 00` | `02 00` |
| `0x10662802` | X `03 00` | `02 00` |
| `0x1066280E` | Y `03 00` | `02 00` |

实现依据见 [实现说明](docs/IMPLEMENTATION.md)。

## 验证范围

第一阶段已经完成：



* [x] 解码官方 Z50 C 2.60 更新包；

* [x] 提取并校验主 `eg` 模块；

* [x] 定位 `d8` 使用的网格模板；

* [x] 只把网格计数从原厂值 3 改为 2；

* [x] 重建模块并独立验证完整文件

尚未全面验证：



* LCD、EVF 在每种显示模式下的像素级位置；

* 电影、回放、睡眠唤醒等不常见路径；

* 更新中断后的必然恢复能力。


详细范围见 [验证记录](docs/VERIFICATION.md)。

## 许可证

本项目的自有代码和文档使用 MIT 许可证。该许可证不适用于尼康固件、

固件派生密钥或其他第三方材料，详见 [NOTICE.md](NOTICE.md)。

## 参考作者与项目

本项目的研究参考了 [WonderLantern 组织](https://github.com/WonderLantern)

及其贡献者公开的项目：



* [wonder-lantern-z5](https://github.com/WonderLantern/wonder-lantern-z5)：

  网格计数字段、3×3 模式取值和公开验证记录；

* [wonder-lantern-z30](https://github.com/WonderLantern/wonder-lantern-z30)：

  EG 模块构建、CRC / 目标校验和风险控制方法；

* [nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool)：

  旧版固件 XOR 密钥研究及 JSON 密钥兼容性。

本项目未包含上述项目的固件、密钥表或完整源码。详细归属和许可证边界见

[参考作者与项目](ACKNOWLEDGEMENTS.md)。

本项目与尼康公司无关联，也未获得尼康授权或背书。
