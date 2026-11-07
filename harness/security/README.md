# Study-local container signal repair — preparation candidate

The default `containers-default-0.66.0` profile denied a UID-1000 Node process signaling its own UID-1000 child (`EACCES`). Kernel audit records identified a stacked peer label containing `crun`. Adding `CAP_KILL` or removing seccomp did not fix it; the AppArmor-only diagnostic control did. No model was run in an unconfined container.

The candidate uses the [upstream containers/common default template](https://github.com/containers/common/blob/a5ccdae846b629b5ceaefa6ffd5c6511409c3487/pkg/apparmor/apparmor_linux_template.go), rendered under a new study-only name, with explicit signal send/receive rules for the **same** profile stacked with `crun` in either label ordering. [A related upstream report](https://github.com/containerd/containerd/issues/12886) describes the stacked-peer mismatch. The requested v0.66.0 source tag was unavailable; this is a pinned upstream-template candidate, not a claim to reproduce the installed policy byte for byte. Source, license and hashes are retained alongside it.

Load only the final candidate before its mechanical tests:

```sh
sudo apparmor_parser -a harness/security/study2-agent.profile
```

If this study-owned profile is already loaded and deliberately being revised, use `-r` with the same file. Existing host/runtime profiles are not modified. The profile name lives in `profile-source.json`; pass it with `--security-opt apparmor=NAME` to study containers. A reboot requires loading the candidate again before dispatch. Unload only after all containers using it have stopped with `sudo apparmor_parser -R harness/security/study2-agent.profile`.

[The signal-control matrix](../../setup/signal-preliminary.json) verifies the candidate retains zero effective capabilities, no-new-privileges, seccomp and no external interfaces. [The repaired runtime replay](https://github.com/joshuarlowry/verified-agent-workflows-study/tree/e1750c4ddcf7614d179e3510303a1fd8e13f001d/setup/r1-container-runtime-signal-repair.json) finishes the public baseline checks with exit 0. [The initial replay](https://github.com/joshuarlowry/verified-agent-workflows-study/tree/e1750c4ddcf7614d179e3510303a1fd8e13f001d/setup/r1-container-runtime-preliminary.json) was mechanically terminated after the cleanup hang and has exit 137; this is infrastructure evidence, not a model failure. Raw logs remain private and are hashed. Different-model profile review, all-role containment/resource tests, actual inference and endpoint snapshot races remain unqualified.
