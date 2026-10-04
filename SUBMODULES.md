# Submodules of droid-hal-version-pdx246

The repo has one submodule. `$ANDROID_ROOT` is the `hybris-23.2` Android tree;
`<sfos>` is the Sailfish workspace that holds it and the local checkouts of the
reference ports.

| path | URL | pin | upstream date |
|---|---|---|---|
| `droid-hal-version` | https://github.com/mer-hybris/droid-hal-version | `09c2745f7cd0eb5f5b941e97272914b03a9cadf2` | 2026-08-08 (merge of PR #28) |

## Why 09c2745 and not the reference's 19c2ba4

- `09c2745` is the current upstream `master`. On 2026-10-04 the GitHub API
  (`/repos/mer-hybris/droid-hal-version/commits`) listed it as the newest
  commit. It is also present locally, as `master` and `origin/master` in
  `<sfos>/pdx235/droid-hal-version-pdx225/droid-hal-version`
  (`git rev-parse origin/master` = 09c2745).
- The reference (sharks-dev droid-hal-version-pdx225, 10 IV and 10 V) pins
  `19c2ba466bef071bfacd62aeba32ea8935dcabfa` (2025-05-21, `git describe`:
  0.0.1-58-g19c2ba4). Between the two pins there is a single change,
  `08bbaa2` "[haptics] Add vibrator_binder define" (`git diff 19c2ba4 09c2745
  --stat`: droid-hal-version.inc, +7/-2). It adds the `have_vibrator_binder`
  case (BuildRequires ngfd-plugin-binder-vibrator) and puts
  `!have_vibrator_binder` into the native and droid-vibrator conditions.
- That change does not affect pdx246's native vibrator setup.
  `have_vibrator_binder` stays undefined, so the native condition
  (droid-hal-version.inc:89 at 09c2745) is still true. Checked offline with the
  SDK's rpmspec 4.16.1.3: the parsed spec gets
  `BuildRequires: ngfd-plugin-native-vibrator`. Pinning the newer commit keeps
  the binder plugin available as a fallback through a single define, and keeps
  the repo on upstream's head.

## Creating it without a network download

The commit is already in the local reference checkout. A clone with
`--no-hardlinks` copies the objects, so the new repo shares nothing with the
reference tree and the reference is only read:

    cd $ANDROID_ROOT/hybris/droid-hal-version-pdx246      # after `git init` and adding this repo's files
    git clone --no-hardlinks \
        <sfos>/pdx235/droid-hal-version-pdx225/droid-hal-version \
        droid-hal-version
    git -C droid-hal-version checkout --detach 09c2745f7cd0eb5f5b941e97272914b03a9cadf2
    git -C droid-hal-version remote set-url origin https://github.com/mer-hybris/droid-hal-version
    git submodule add https://github.com/mer-hybris/droid-hal-version droid-hal-version
    git submodule status       # expect: 09c2745f7cd0... droid-hal-version (0.0.1-60-g09c2745)

The `git submodule add` reuses the existing repo at that path ("Adding existing
repo at 'droid-hal-version' to the index") and generates this `.gitmodules`,
which has the same shape as the reference's:

    [submodule "droid-hal-version"]
    	path = droid-hal-version
    	url = https://github.com/mer-hybris/droid-hal-version

The expected `git describe` value was checked in the local reference checkout:
`git describe --tags 09c2745` prints 0.0.1-60-g09c2745.

The submodule path has to be exactly `droid-hal-version` at the repo root. The
spec's `%include droid-hal-version/droid-hal-version.inc` is resolved relative to
the repo root, which is where buildversion runs mb2 (dhd helpers/util.sh:162-167).
