# droid-hal-version-pdx246

Sailfish OS version package for the Sony Xperia 10 VI (pdx246; XQ-ES54 and
XQ-ES72), built on the LineageOS 23.2 / Android 16 base (`hybris-23.2`).

It builds one package, `droid-hal-version-pdx246`. The package installs
`/usr/lib/hw-release` and the `/etc/hw-release` symlink to it, and it requires
`patterns-sailfish-device-configuration-pdx246`. The packaging is in the
`droid-hal-version` submodule (mer-hybris/droid-hal-version, pinned at
`09c2745`). `rpm/droid-hal-version-pdx246.spec` only sets the device macros.

`NOTES.md` explains the macros and how the build finds this repo;
`SUBMODULES.md` explains the submodule pin.

## Checkout

The repo must be checked out at `$ANDROID_ROOT/hybris/droid-hal-version-pdx246`,
with its submodule.

`build_packages.sh -v` searches `hybris/` for `droid-hal-version-pdx246.spec`.
It changes into the parent of the `rpm/` directory where it finds the file, and
afterwards changes back up two levels. So keep exactly one copy of this repo
under `hybris/`, and keep it two levels deep.

## Build

This package is one step of the port's build. The whole order is:

1. On the host, in `$ANDROID_ROOT`, with the hybris patches applied:

       export PORT_ARCH=aarch64   # droidmedia's target list depends on it
       source build/envsetup.sh
       lunch lineage_pdx246-bp4a-userdebug
       make hybris-hal droidmedia vendor_dlkmimage audio.hidl_compat.default

2. In the Platform SDK, from `$ANDROID_ROOT`:

       rpm/dhd/helpers/build_packages.sh -d      # droid-hal-pdx246
       rpm/dhd/helpers/build_packages.sh -c      # droid-config-pdx246
       git clone --recurse-submodules https://github.com/mer-hybris/pulseaudio-modules-droid.git hybris/mw/pulseaudio-modules-droid
       git -C hybris/mw/pulseaudio-modules-droid checkout 65edd31f62f22e2eec1f765608ca9c6ae5c4af7b   # 14.2.106
       rpm/dhd/helpers/build_packages.sh -o --mw # default middleware set, offline
       rpm/dhd/helpers/build_packages.sh --mw=https://github.com/sailfish-on-nabu/parse-android-dynparts
       rpm/dhd/helpers/build_packages.sh --mw=https://github.com/sailfishos/sensorfw --spec=rpm/sensorfw-qt5-binder.spec
       rpm/dhd/helpers/build_packages.sh -g      # droidmedia, gst-droid
       rpm/dhd/helpers/build_packages.sh -o -N --mw=droid-hal-img-boot-pdx246
       rpm/dhd/helpers/build_packages.sh -v      # this repo
       rpm/dhd/helpers/build_packages.sh -i      # the image

   - `--mw` builds libhybris, pulseaudio-modules-droid,
     pulseaudio-modules-droid-hidl, mce-plugin-libhybris and
     qt5-qpa-hwcomposer-plugin. pulseaudio-modules-droid is kept at 14.2.106
     (commit 65edd31f62f22e2eec1f765608ca9c6ae5c4af7b), the version recommended
     for Sailfish OS 5.1. Before the `--mw` run, clone it into
     `hybris/mw/pulseaudio-modules-droid` and check out that commit, then run
     `--mw` with `-o` (`build_packages.sh -o --mw`): without `-o`, `--mw` runs
     `git pull` in each repo first and would move it to a newer release.
   - img-boot (`hybris/mw/droid-hal-img-boot-pdx246`) is built through `--mw`,
     not with `-b`. Only the `--mw` route runs dhd's img-boot preparation: it
     removes the installed img-boot from the build target and installs
     `droid-hal-pdx246-kernel` and `droid-hal-pdx246-kernel-modules` again. With
     `-b` that step is skipped, and after a `-d` rebuild the target can end up
     with the old img-boot in place of `-kernel-modules` (img-boot Provides and
     Obsoletes it), so the img-boot build finds no modules. `-o` stops `--mw`
     from running `git pull` in the repo, and `-N` skips the tag check, so the
     untagged repo keeps the kernel version as its Version.

`-v` needs the packages from `-d` (droid-hal, droid-hal-kernel), `-c`
(droid-config and its sub-packages), the default `--mw` set and the sensorfw
binder build (hybris-libsensorfw-qt5). It also needs
`ngfd-plugin-native-vibrator`; if the build target's repositories do not have
it, build it with `--mw` first (NOTES.md, TODO B1). The package is written to
`$ANDROID_ROOT/droid-local-repo/pdx246`.
