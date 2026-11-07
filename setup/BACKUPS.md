# Preparation artifact recovery

Sanitized raw preparation artifacts live in the private `verified-agent-workflows-artifacts` repository. Public study evidence remains in this repository. Credentials, private agent homes, dependencies/build/browser caches and disposable test databases are excluded. Approved corpus database packages must be retained under a `corpus` or `context-packages` path. Official raw source archives are retained.

Earlier full checkpoints remain unchanged. New checkpoints contain changed/new files, a complete current inventory and the parent archive's SHA-256. Restore follows that verified chain and excludes paths removed from the latest inventory. Large archives retain their existing split-part manifests; the restore tool verifies and reassembles missing originals into `.restore-cache` in the private checkout.

After cloning both repositories, use the sidecar metadata to select a checkpoint. Restore to a **new** directory:

```sh
python3 scripts/archive_preparation_snapshot.py \
  --destination /path/to/verified-agent-workflows-artifacts \
  --restore-archive checkpoints/CHOSEN.tar.gz \
  --target /new/private/restore-directory
```

Use the script revision matching the checkpoint's recorded activation/source hash. The tool verifies archive/part hashes and every restored file against the latest inventory. It does not restore credentials or restart processes. Active files in a passive checkpoint can be partial; immutable endpoint source and logs remain distinct from passive snapshots. Revalidate launch state before resuming a controller.

[Activation](incremental-backup-activation.json), [13 synthetic checks](incremental-backup-checks.json) and [actual checkpoint restore](incremental-backup-real-restore.json) record the tested recovery scope. These are artifact-transport checks, not study acceptance results.
