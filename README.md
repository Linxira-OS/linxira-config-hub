# Linxira Config Hub

Configuration and diagnostics tools for Linxira OS.

The current supported surface is `cli/linxira-config` for administrator-facing
source, runtime, SSH, network and controlled configuration management. General
software management is owned by Shelly, while curated application setup is owned
by Quick System Software Setup and its `linxira-components` transaction backend.
Config Hub does not contain a software-center implementation or expose software
installation commands. Its mirror commands cover
Arch, npm, PyPI, AUR, Go modules and explicitly enabled Flatpak remotes.

## Catalog queries

Catalog commands are read-only and accept catalog IDs, never package names or
commands:

```console
linxira-config catalog software --all
linxira-config catalog component --status partial
linxira-config catalog bundle show kde-plasma
```

Catalog v2 compatibility maps `software` to `applications`, `component` to the
legacy `profiles` metadata, and `bundle` to `desktopBundles`. The CLI does not
expand or apply any of these records. By default lists only show `installed`,
`partial`, `external`, `pending`, `drifted`, and `reboot-required`; `--all`
also shows `not-installed` entries. `--status` accepts those states plus
`not-installed` and `unavailable`.

When `/var/lib/linxira/catalog/state-v1.json` is absent, package observation is
reported as `external`, `partial`, or `not-installed`. A state file may provide
managed or pending states using this fixed shape:

```json
{
  "catalogStateVersion": 1,
  "items": [
    {"kind": "software", "id": "firefox", "status": "installed"}
  ]
}
```

`LINXIRA_CATALOG_STATE_PATH` may select another state file for testing.

## SSH quick start (turn this machine into a server)

One command sets up remote access (installs `openssh` if missing, enables and
starts `sshd`, explicitly allows password authentication, opens the firewall
when UFW is active, and prints the connection line):

```console
sudo linxira-config ssh on   # prints: Connect: ssh <user>@<ip>
linxira-config ssh status    # verify: SSH server: RUNNING
```

Generate a key pair on the client you connect *from*:

```console
linxira-config ssh key generate            # Ed25519, ~/.ssh/id_ed25519
linxira-config ssh key show                # copy the public key line
```

Authorize it on the server (plain public keys only, by design):

```console
echo 'ssh-ed25519 AAAA... user@host' > /tmp/key.pub
linxira-config ssh authorized add /tmp/key.pub && rm /tmp/key.pub
linxira-config ssh authorized list
```

Connect from the client (IP shown in `ssh status` → `Connect:`):

```console
ssh user@server-ip
```

Security notes: disable `PasswordAuthentication` in
`/etc/ssh/sshd_config` before exposing to the public internet, and keep the
firewall on. See the full tutorial at
<https://linxira-os.github.io/docs/remote-access/> (or `/zh/docs/remote-access/`).

## Headless mode (desktop ⇄ server, runtime switch)

`headless on/off/status` switches the running system between the KDE desktop
and a headless server state, freeing the memory the desktop would otherwise
consume for computation tasks:

```console
linxira-config headless on       # desktop disabled from next boot
linxira-config headless on now   # switch immediately (interactive confirm)
linxira-config headless off      # restore desktop from next boot
linxira-config headless off now  # switch back immediately
linxira-config headless status   # current target (multi-user vs graphical)
```

`on now` stops the display manager and terminates the current desktop session
(unsaved data is lost — the CLI asks for confirmation on a TTY). The switch is
`systemctl isolate multi-user.target`; the reverse restarts SDDM. Use SSH or a
TTY to switch back.

## SSH keys

`ssh key list/show/fingerprint/generate/remove` manages named Ed25519 key pairs
for the invoking target user. Names are plain basenames, existing keys are never
overwritten, symlinked SSH paths are rejected, generation prompts for a
passphrase, and removal requires `--yes`.

`ssh authorized list/add/remove` manages the same user's `authorized_keys`.
Only one plain public key without `authorized_keys` options is accepted per add;
removal uses an exact SHA256 fingerprint and requires `--yes`. This prevents
forced-command or environment options from becoming a shell execution path.
Existing optioned entries are visible as `optioned` and can be removed, but the
CLI never creates them.


## Software stacks & environment variables (WSL one-stop entry)

`stack` is an explicit forwarding bridge to `linxira-component-manager` — the
same plan → confirm → apply transaction chain used by the GUI and AI agents.
Installation logic stays single-sourced there; the direct `linxira-config
install <pkg>` entrypoint remains rejected.

```bash
linxira-config stack list                 # installer-visible leaves (+ --json)
linxira-config stack install component-uv --yes --dry-run
linxira-config stack install component-latex component-java --yes
linxira-config stack tui                  # curses TUI of component-manager
```

`env` manages `/etc/profile.d/linxira-env.sh` (root, 0644):

```bash
linxira-config env set GOPROXY https://goproxy.cn,direct
linxira-config env get GOPROXY            # (+ --json)
linxira-config env list [--json]
linxira-config env unset GOPROXY
```

`linxira-config tui` opens a pure-bash numbered menu (zero dependencies) that
dispatches to the very same command implementations.

## Workspace guard

`workspace-guard` protects a work directory (`.git` included) from an agent that
runs with the user's full permissions. It is off until a root administrator turns
it on, and it is deliberately unreadable to the agent afterwards.

```console
sudo linxira-config workspace-guard enable     # pick a disk, create the ext4 store, register, start the timer
linxira-config workspace-guard status          # configuration, store, timer
linxira-config workspace-guard status --json   # same, one line of JSON
sudo linxira-config workspace-guard disable    # stop the timer, keep every stored recovery point
linxira-config workspace-guard handbook        # AI-readable handbook manifest
```

`enable` is idempotent: it skips the partitioning steps when the configuration is
already present, so an interrupted run resumes at the check instead of partitioning
again. A partition it created is never removed automatically — deleting a
partition table is destructive and stays a human decision.

The store lives on a partition that is deliberately **not** added to `/etc/fstab`:
it is not mounted at boot, so without root the agent cannot reach or alter any
recovery point. `/etc/linxira/workspace-guard.conf` is `root:root 0600`; a
non-root `status` reports "present but not readable" instead of a permission
traceback.

Day-to-day operations live in `linxira-components guard`
(`status`/`list` read-only, `snapshot`/`restore` behind a Polkit prompt).
Restoring always writes a new directory and never overwrites the live workspace.

## Runtime contract

- Bash
- `jq`
- `pacman` and standard Arch system tools
- `/usr/share/linxira/catalog/catalog-v3.json` from `linxira-catalog`

Set `LINXIRA_CATALOG_PATH` to validate the CLI against a catalog outside an
installed Linxira system.

Flatpak remotes remain disabled by default. `mirror flatpak set flathub` is an
explicit opt-in operation and requires the `flatpak` client.

Go proxy changes are persisted through `go env -w`; the configured proxy is
used with `direct` fallback. `mirror go reset` restores `proxy.golang.org`.

Conda configuration is intentionally limited to Miniforge. The CLI refuses to
modify a generic Conda installation and only allows the reviewed channel IDs
`conda-forge` and `bioconda`; both can be enabled together with strict channel
priority. Anaconda `defaults` is not configured or enabled by Linxira.

## License

MIT. See `LICENSE`.

---

## 简体中文

Linxira OS 的配置与诊断工具。

当前受支持的界面是 `cli/linxira-config`，面向管理员提供来源、运行时、SSH、网络与受控配置管理。通用软件管理由 Shelly 负责，策展应用安装由 Quick System Software Setup 及其 `linxira-components` 事务后端负责。Config Hub 不包含软件中心实现，也不暴露软件安装命令。其镜像命令覆盖 Arch、npm、PyPI、AUR、Go modules 以及显式启用的 Flatpak 远端。

## 目录查询

目录命令是只读的，接受目录 ID，绝不接受包名或命令：

```console
linxira-config catalog software --all
linxira-config catalog component --status partial
linxira-config catalog bundle show kde-plasma
```

Catalog v2 兼容层把 `software` 映射到 `applications`，把 `component` 映射到旧的 `profiles` 元数据，把 `bundle` 映射到 `desktopBundles`。CLI 不展开也不应用这些记录。默认情况下列表只显示 `installed`、`partial`、`external`、`pending`、`drifted` 与 `reboot-required`；`--all` 还会显示 `not-installed` 条目。`--status` 接受这些状态外加 `not-installed` 与 `unavailable`。

当 `/var/lib/linxira/catalog/state-v1.json` 不存在时，包观察结果报告为 `external`、`partial` 或 `not-installed`。状态文件可以按下面这个固定形状提供 managed 或 pending 状态：

```json
{
  "catalogStateVersion": 1,
  "items": [
    {"kind": "software", "id": "firefox", "status": "installed"}
  ]
}
```

`LINXIRA_CATALOG_STATE_PATH` 可为测试选择另一个状态文件。

## SSH 快速上手（把这台机器变成服务器）

一条命令开通远程访问（缺少则安装 `openssh`，启用并启动 `sshd`，显式允许密码认证，UFW 激活时放行防火墙，并打印连接行）：

```console
sudo linxira-config ssh on   # prints: Connect: ssh <user>@<ip>
linxira-config ssh status    # verify: SSH server: RUNNING
```

在你要用来连接的*客户端*上生成密钥对：

```console
linxira-config ssh key generate            # Ed25519, ~/.ssh/id_ed25519
linxira-config ssh key show                # copy the public key line
```

在服务器上授权（设计上只接受纯公钥）：

```console
echo 'ssh-ed25519 AAAA... user@host' > /tmp/key.pub
linxira-config ssh authorized add /tmp/key.pub && rm /tmp/key.pub
linxira-config ssh authorized list
```

从客户端连接（IP 见 `ssh status` 的 `Connect:`）：

```console
ssh user@server-ip
```

安全提示：在暴露到公网之前，先在 `/etc/ssh/sshd_config` 中禁用 `PasswordAuthentication`，并保持防火墙开启。完整教程见
<https://linxira-os.github.io/docs/remote-access/>（或 `/zh/docs/remote-access/`）。

## 无头模式（桌面 ⇄ 服务器，运行时切换）

`headless on/off/status` 在 KDE 桌面与无头服务器状态之间切换运行中的系统，把桌面原本占用的内存释放给计算任务：

```console
linxira-config headless on       # desktop disabled from next boot
linxira-config headless on now   # switch immediately (interactive confirm)
linxira-config headless off      # restore desktop from next boot
linxira-config headless off now  # switch back immediately
linxira-config headless status   # current target (multi-user vs graphical)
```

`on now` 会停止显示管理器并终止当前桌面会话（未保存的数据会丢失 —— CLI 在 TTY 上会要求确认）。切换动作是 `systemctl isolate multi-user.target`；反向操作会重启 SDDM。请使用 SSH 或 TTY 切换回来。

## SSH 密钥

`ssh key list/show/fingerprint/generate/remove` 为被调用的目标用户管理命名的 Ed25519 密钥对。名称是纯 basename，现有密钥绝不会被覆盖，符号链接的 SSH 路径被拒绝，生成时会提示输入口令，移除需要 `--yes`。

`ssh authorized list/add/remove` 管理同一用户的 `authorized_keys`。每次 add 只接受一个不带 `authorized_keys` 选项的纯公钥；移除使用精确的 SHA256 指纹并需要 `--yes`。这防止 forced-command 或 environment 选项成为 shell 执行路径。带选项的现有条目以 `optioned` 显示，可以移除，但 CLI 绝不创建它们。


## 软件栈与环境变量（WSL 一站式入口）

`stack` 是到 `linxira-component-manager` 的显式转发桥 —— 与 GUI 和 AI 代理使用的相同 plan → confirm → apply 事务链。安装逻辑保持单源于彼处；直接的 `linxira-config install <pkg>` 入口仍然被拒绝。

```bash
linxira-config stack list                 # installer-visible leaves (+ --json)
linxira-config stack install component-uv --yes --dry-run
linxira-config stack install component-latex component-java --yes
linxira-config stack tui                  # curses TUI of component-manager
```

`env` 管理 `/etc/profile.d/linxira-env.sh`（root，0644）：

```bash
linxira-config env set GOPROXY https://goproxy.cn,direct
linxira-config env get GOPROXY            # (+ --json)
linxira-config env list [--json]
linxira-config env unset GOPROXY
```

`linxira-config tui` 打开一个纯 bash 编号菜单（零依赖），分发到完全相同的命令实现。

## 工作区守护

`workspace-guard` 保护工作目录（含 `.git`）免受以用户完整权限运行的 agent 破坏。在 root 管理员开启之前它处于关闭状态，开启之后对 agent 刻意不可读。

```console
sudo linxira-config workspace-guard enable     # pick a disk, create the ext4 store, register, start the timer
linxira-config workspace-guard status          # configuration, store, timer
linxira-config workspace-guard status --json   # same, one line of JSON
sudo linxira-config workspace-guard disable    # stop the timer, keep every stored recovery point
linxira-config workspace-guard handbook        # AI-readable handbook manifest
```

`enable` 是幂等的：当配置已存在时跳过分区步骤，因此被中断的运行会从检查处继续，而不是再次分区。它创建的分区绝不会被自动删除 —— 删除分区表是破坏性操作，始终由人来决定。

存储位于一个刻意**不**加入 `/etc/fstab` 的分区上：开机不挂载，因此没有 root 的 agent 无法触及或篡改任何恢复点。`/etc/linxira/workspace-guard.conf` 为 `root:root 0600`；非 root 的 `status` 会报告 "present but not readable" 而不是权限回溯。

日常操作位于 `linxira-components guard`（`status`/`list` 只读，`snapshot`/`restore` 需经过 Polkit 提示）。恢复总是写入新目录，从不覆盖活动工作区。

## 运行时契约

- Bash
- `jq`
- `pacman` 与标准 Arch 系统工具
- 来自 `linxira-catalog` 的 `/usr/share/linxira/catalog/catalog-v3.json`

设置 `LINXIRA_CATALOG_PATH` 可以针对已安装 Linxira 系统之外的 catalog 校验 CLI。

Flatpak 远端默认保持禁用。`mirror flatpak set flathub` 是显式选择加入的操作，且需要 `flatpak` 客户端。

Go 代理变更通过 `go env -w` 持久化；配置的代理与 `direct` 回退一起使用。`mirror go reset` 恢复 `proxy.golang.org`。

Conda 配置刻意仅限 Miniforge。CLI 拒绝修改通用 Conda 安装，只允许经过评审的通道 ID `conda-forge` 与 `bioconda`；两者可以在严格通道优先级下同时启用。Anaconda `defaults` 不由 Linxira 配置或启用。

## 许可证

MIT。见 `LICENSE`。
