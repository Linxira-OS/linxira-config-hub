---
name: linxira-config
description: "Configure Linxira OS from the command line: system status, power, SSH, firewall, mirrors, diagnostics, GPU, runtime, environment, and software stacks. Use when the user asks to inspect or change system settings, or when a crash/debug task needs host configuration context."
skill_class: system
load_policy: on-demand
risk_tags: [system, privilege]
---

# Linxira config (linxira-config)

`linxira-config` is the single system configuration CLI on Linxira OS. The
machine-readable capability list is authoritative:

```bash
linxira-config capabilities            # JSON manifest
linxira-config capabilities --path     # manifest path
```

Installed copy: `/usr/share/linxira/agent/capabilities.json`.
This skill: `/usr/share/linxira/agent/skills/linxira-config/SKILL.md`.

## Rules

1. **Read before writing.** Prefer `status`, `info`, `power status`,
   `ssh status`, `security status`, `net diag`, `gpu info`, `runtime status`,
   `stack list`, `catalog ...`.
2. **Mutating commands need an explicit user decision.** The manifest marks
   them with `"mutating": true` and `"privilege": "root"`. Ask the user first,
   state exactly what will change, then run it in a terminal where the user can
   authenticate. Never capture, echo, or store the sudo password.
3. **Do not invent flags.** Use only the argv in the manifest or the documented
   syntax from `linxira-config <command> --help`.
4. **One change at a time.** Run the command, read its output, then continue.
   Do not chain unrelated mutating commands.
5. **On failure**, collect the command output and `journalctl` lines relevant to
   the service. Do not retry a destructive command blindly.
6. **JSON first** when a command supports `--json`; parse it instead of scraping
   human text.

## Common read-only examples

```bash
linxira-config status
linxira-config info
linxira-config power status
linxira-config ssh status
linxira-config security status
linxira-config net diag
linxira-config gpu info
linxira-config runtime status
linxira-config stack list
linxira-config workspace-guard status --json
```

## Privileged examples (ask first)

```bash
sudo linxira-config ssh on
sudo linxira-config ssh harden
sudo linxira-config ssh password on --yes
sudo linxira-config ssh off
sudo linxira-config security ufw on
sudo linxira-config security ufw allow 22
```

`ssh harden` refuses without a valid `authorized_keys` entry. It changes the
managed `10-linxira.conf`, validates with `sshd -t`, and reloads sshd. Keep an
existing session open until a new key-only login succeeds.

## Scope boundaries

- `linxira-config` does not own package installation; use
  `linxira-component-manager` / `linxira-config stack`.
- It does not install or remove GPU drivers directly; `gpu` reports and routes.
- It does not change bootloader or partition layout.
