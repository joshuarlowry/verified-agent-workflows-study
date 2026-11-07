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

The dependency image is preserved separately from source/log checkpoints because it contains roughly 3.4 GB of installed tools and dependencies. [Image preservation evidence](dependency-image-preservation.json) records the exact image, OCI archive and compressed-file hashes, an independent-storage load that reproduced the image ID, and publication status. The raw upstream package material remains in the **private** artifact repository. This is a recovery artifact, not study launch qualification.

When its receipt confirms publication, download the assets from the private release `dependency-image-3005436d2c76` in `joshuarlowry/verified-agent-workflows-artifacts`. Verify each SHA256, concatenate parts in listed order if applicable, decompress to the OCI tar and verify its SHA256, then use `podman load --input ARCHIVE.tar`. The loaded image ID must match the receipt. Preserve both the original receipt and any publication-recovery receipt; a failed first upload is not erased by later recovery. [Preservation controller](../scripts/preserve_dependency_image.py).
