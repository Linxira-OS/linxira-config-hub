# linxira-config-hub · Agent 开发规范

> **档位**:A 档 · 系统源仓(带 `VERSION` + `.github/workflows/release.yml`)。
> **本仓职责**:面向管理员的配置与诊断工具 `linxira-config`(catalog 查询 / ssh / headless / stack / env / mirror / workspace-guard)。
> 通用条款见工作区总纲 `f:\Linxira-OS\AGENTS.md`;发布/测试口径见 `linxira-os/docs/RELEASE_STANDARD.md`。本文件只写本仓特有约定。

## 职责与边界

- **负责**:受支持的界面 `cli/linxira-config`(bash),提供来源/运行时/SSH/网络/受控配置管理;catalog 只读查询;`headless` 桌面⇄服务器切换;`env` 管理 `/etc/profile.d/linxira-env.sh`(root 0644);`mirror`(Arch/npm/PyPI/AUR/Go/显式启用的 Flatpak 远端);`tui`(纯 bash 菜单);`workspace-guard`(工作区守护配置与状态)。
- **拥有诊断与设置入口**:只读诊断、状态查询与设置入口在本仓。
- **不负责软件管理与安装**:通用软件管理归 Shelly;策展应用安装归 Quick System Software Setup 及其 `linxira-components` 后端。本仓**不含软件中心实现、不暴露软件安装命令**;`linxira-config install <pkg>` 入口被拒绝。
- `stack` 只是到 `linxira-component-manager` 的**显式转发桥**(plan → confirm → apply);安装逻辑单源于 `linxira-components`;`workspace-guard` 的日常操作在 `linxira-components guard`。

## 目录布局

```
cli/linxira-config      主 CLI(bash,内嵌 VERSION 串)
src/                    Python 测试支撑/实现
tests/                  test_cli_logs / test_catalog_contract / test_stack_env_tui
data/linxira-config.desktop
```

## 本地校验

CI(`.github/workflows/ci.yml`)先校验 **`cli/linxira-config` 内嵌 `VERSION="..."` 与 `VERSION` 文件一致**,再:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src
```

(CI 使用 Python 3.13。)

## 运行时契约

- 依赖:Bash、`jq`、`pacman` 与标准 Arch 系统工具、来自 `linxira-catalog` 的 `/usr/share/linxira/catalog/catalog-v3.json`。
- 测试可用 `LINXIRA_CATALOG_PATH` 指向外部 catalog,`LINXIRA_CATALOG_STATE_PATH` 指向另一状态文件。

## 版本与发布

- 版本唯一来源是根目录 `VERSION`(当前 2.5.2);`cli/linxira-config` 内嵌的 `VERSION="..."` 必须同步(CI 会拒)。
- 提交 `VERSION` 变更即触发 `.github/workflows/release.yml` 走全自动发布链。**禁止手工 bump**。

## 禁区

- catalog 命令**只读**,只接受 catalog ID,**绝不接受包名或命令**;不得展开或应用记录。
- `ssh authorized add` 只接受一个不带 `authorized_keys` 选项的纯公钥;移除用精确 SHA256 指纹且需 `--yes`——不得引入 forced-command/环境选项执行路径。
- Flatpak 远端默认禁用,`mirror flatpak set flathub` 是显式 opt-in;Conda 仅限 Miniforge 的 `conda-forge` / `bioconda`,拒绝通用 Conda 与 Anaconda `defaults`。
- 需要 root 的操作(`ssh on`、`headless on now`、`workspace-guard enable`)按既有交互确认;`on now` 会终止桌面会话、丢失未保存数据——不得静默执行。
- 不得新增直连软件安装路径;提权只走 `linxira-components` + polkit。