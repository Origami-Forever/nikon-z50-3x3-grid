# 参考作者与项目

本项目的 Z50 补丁由本项目贡献者独立定位和实现，但研究过程参考了
**WonderLantern 组织及其贡献者**公开的项目、文档和验证记录。感谢他们公开
分享 Nikon EXPEED 6 固件研究经验。

## WonderLantern

组织主页：

- [WonderLantern](https://github.com/WonderLantern)

### wonder-lantern-z5

- 项目：[WonderLantern/wonder-lantern-z5](https://github.com/WonderLantern/wonder-lantern-z5)
- 参考内容：
  - 网格模板中 X/Y 计数字段的位置；
  - 3×3 模式把两个计数设为 `2`；
  - 3×3、4×4 和 2×2 网格功能的公开说明与实机验证记录。
- 本项目没有复制该项目的完整源码或固件。
- 该项目包含自有及第三方材料，许可证以该上游仓库中的实际文件为准。

### wonder-lantern-z30

- 项目：[WonderLantern/wonder-lantern-z30](https://github.com/WonderLantern/wonder-lantern-z30)
- 参考内容：
  - 独立 EG 模块的构建与验证流程；
  - 固件包、模块 CRC 和补丁目标校验的方法；
  - 刷机风险、回退固件和相机端验证的公开记录。
- 本项目没有包含该项目的 Z30 固件、菜单代码或修改后升级文件。
- 该项目采用 MIT 与 Wonder Lantern Community License 的混合授权，具体以
  上游仓库的 `LICENSE` 和 `THIRD_PARTY_NOTICES.md` 为准。

### nikon-fw-key-tool

- 项目：[WonderLantern/nikon-fw-key-tool](https://github.com/WonderLantern/nikon-fw-key-tool)
- 用途：提供尼康旧版固件 XOR 表的恢复、解密和校验研究。
- 本项目支持读取其 JSON 密钥文件，以便用户使用自行取得的本地密钥。
- 上游项目采用 GPL-3.0；本项目没有包含或再分发其源码、二进制或恢复出的
  密钥表。

## Nikon

Nikon、Z 50 及相关名称是 Nikon Corporation 的商标。本项目仅使用这些名称
说明兼容设备，与 Nikon Corporation 无关联，也未获得其授权或背书。

## 范围说明

上述参考项目并非本项目的官方发布者，也不对本项目作任何保证。各项目的
代码、文档、固件和第三方材料继续受其各自许可证约束。
