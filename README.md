# droid-hal-version-pdx246

Sailfish OS version package for the Sony Xperia 10 VI (pdx246; XQ-ES54 and
XQ-ES72), built on the LineageOS 23.2 / Android 16 base (`hybris-23.2`).

It builds one package, `droid-hal-version-pdx246`. The package installs
`/usr/lib/hw-release` and the `/etc/hw-release` symlink to it, and it requires
`patterns-sailfish-device-configuration-pdx246`, which pulls in the whole
adaptation. The packaging is in the `droid-hal-version` submodule
(mer-hybris/droid-hal-version); `rpm/droid-hal-version-pdx246.spec` only sets
the device macros. Building and installing the port are described in
[main](https://github.com/sailfishos-sony-pdx246/main): `BUILD.md` (this
repository is its step `v`) and `INSTALL.md`.

## Checkout

The repo must be checked out at `$ANDROID_ROOT/hybris/droid-hal-version-pdx246`,
with its submodule.

`build_packages.sh -v` searches `hybris/` for `droid-hal-version-pdx246.spec`.
It changes into the parent of the `rpm/` directory where it finds the file, and
afterwards changes back up two levels. So keep exactly one copy of this repo
under `hybris/`, and keep it two levels deep.

## Build

`-v` comes last before the image: it builds against the packages of all earlier
steps (droid-hal, img-boot, droid-config and the middleware) and against
sensorfw's binder backend and `ngfd-plugin-native-vibrator` from Jolla's
repositories. On a fresh build target, install `droid-config-pdx246` by name
first (BUILD.md's `build-packages-sdk.sh` does that in step `v`): it obsoletes
Jolla's usb-moded-defaults, and zypper's non-interactive mode refuses that
vendor change when the package is only pulled in as a build dependency. The
Release is a build timestamp, so every build gets a new version; the package is
written to `$ANDROID_ROOT/droid-local-repo/pdx246`.
