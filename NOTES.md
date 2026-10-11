# droid-hal-version-pdx246: design notes (as of 2026-10-04)

The repo content is `rpm/droid-hal-version-pdx246.spec`, `.gitignore`,
`README.md`, `REUSE.toml`, `LICENSES/` (BSD-3-Clause, CC-BY-SA-4.0), this file,
`SUBMODULES.md` and the submodule (see SUBMODULES.md).

Placeholders used below:
- `$ANDROID_ROOT` = the `hybris-23.2` Android tree (as in `~/.hadk.env`).
- `<sfos>` = the Sailfish workspace that holds `$ANDROID_ROOT` and the local
  checkouts of the reference ports (`<sfos>/pdx225`, `<sfos>/pdx235`).
- `<lineageos tree>` = the LineageOS 23.2 checkout of this device.
- `$PLATFORM_SDK_ROOT` = the Platform SDK install root (the HADK variable).

Abbreviations:
- `dhv` = mer-hybris/droid-hal-version at 09c2745. The local copy is
  `<sfos>/pdx235/droid-hal-version-pdx225/droid-hal-version`, and line numbers
  come from `git show 09c2745:droid-hal-version.inc`.
- `dhd` = mer-hybris/droid-hal-device at be67bbc, in
  `<sfos>/pdx235/droid-hal-pdx225/dhd`. Upstream master 775f6c0 changes only
  helpers/makefstab against it, so helpers/util.sh and helpers/build_packages.sh
  are the same on both.

## 1. How `build_packages.sh -v` finds and builds this repo

| step | code | what it means for pdx246 |
|---|---|---|
| The script must be run from `$ANDROID_ROOT` | dhd helpers/build_packages.sh:125-128 (`[ ! -d rpm/dhd ]` → die) | run it from `$ANDROID_ROOT` (the path set in `~/.hadk.env`) |
| `-v` sets BUILDVERSION=1; a run with no arguments also sets it | build_packages.sh:44, :59, :67-74, :104 | `-v` runs after the `-d/-c/--mw/-g` blocks of the same call (:348-351) |
| `buildversion()` sets PKG=droid-hal-version-$DEVICE | util.sh:160-161 | PKG = `droid-hal-version-pdx246` (DEVICE=pdx246 in ~/.hadk.env) |
| `dir=$(dirname $(find hybris -name $PKG.spec))` | util.sh:162 | it searches all of `$ANDROID_ROOT/hybris` (including `hybris/mw/*`). Exactly ONE `droid-hal-version-pdx246.spec` may exist there; with two, `dirname` prints two lines and the `cd` fails. A copy outside `$ANDROID_ROOT` does not interfere. |
| `cd $dir/..` | util.sh:163 | the spec must sit in an `rpm/` directory directly below the repo root |
| `initlog $PKG $(dirname "$PWD")` | util.sh:164, :83-90 | the log is `$ANDROID_ROOT/hybris/droid-hal-version-pdx246.log` |
| `rm -f $LOCAL_REPO/droid-hal-version-*` | util.sh:166, :69 | old builds in `droid-local-repo/pdx246` are removed first |
| `build $PKG rpm/$PKG.spec` → `mb2 -s rpm/droid-hal-version-pdx246.spec -t sony-pdx246-aarch64 --package-timeline --output-dir droid-local-repo/pdx246 build --no-check` | util.sh:167, :324-348 (`--package-timeline` because PKG matches `droid-hal-*`, :336) | the target `sony-pdx246-aarch64` exists (`$PLATFORM_SDK_ROOT/targets/sony-pdx246-aarch64`, os-release 5.1.0.11) |
| `cd ../../` | util.sh:168 | assumes the repo is exactly two levels below `$ANDROID_ROOT`, so it must be `hybris/droid-hal-version-pdx246` and not `hybris/mw/...` |
| mb2 runs in the repo root | (same) | the spec's `%include droid-hal-version/droid-hal-version.inc` resolves against the repo root, so the submodule path must be `droid-hal-version` |

The image pulls the package in through droid-config's pattern
(`Requires: droid-hal-version-@DEVICE@`, droid-hal-configs
patterns/templates/patterns-sailfish-device-adaptation-@DEVICE@.inc:12 at
1dae7f2). droid-config-pdx246 has to keep that line.

## 2. What the reference's two specs did, and why there is one here

sharks-dev/droid-hal-version-pdx225 (local copies in `<sfos>/pdx225/` and
`<sfos>/pdx235/`, which are identical per `diff -r`; HEAD 5ddcffd) carries
`rpm/droid-hal-version-xqcc72.spec` (Xperia 10 IV) and
`rpm/droid-hal-version-xqdc72.spec` (Xperia 10 V). The two differ only in
`rpm_device` and `device_pretty`. One repo serves two devices: each device's
manifest checks it out under its own path
(`sailfish-on-murray/manifest.xml:20` → `hybris/droid-hal-version-xqcc72`,
`sailfish-on-zambezi/manifest.xml:20` → `hybris/droid-hal-version-xqdc72`), and
buildversion picks the spec that matches `$DEVICE`. They set `rpm_device`
rather than `device` because their Sailfish DEVICE (xqcc72/xqdc72) differed
from the Android codename (FAMILY/HABUILD_DEVICE pdx225/pdx235).

pdx246 builds a single device. DEVICE=pdx246 is used everywhere, and one image
serves XQ-ES54 and XQ-ES72, so there is one spec, named after `$DEVICE`, and it
uses the template's `%define device` form (dhv
droid-hal-version-@DEVICE@.spec.template:3). The .inc then defaults
`rpm_device`/`rpm_vendor` to `device`/`vendor` (dhv:19-24).

The reference also defined `droid_target_aarch64 1`. dhv never reads it
(`git grep droid_target 09c2745` finds nothing). It belongs in
droid-hal-pdx246.spec, where dhd stops without it (droid-hal-device.inc:433-438).
It is left out here.

## 3. Macros: what is defined and why

The .inc tests whether a macro is defined (`0%{?macro:1}`), never its value.
This was checked by parsing a copy of the spec with the Platform SDK's rpmspec
4.16.1.3:
- `%define have_led 0` still adds `BuildRequires: mce-plugin-libhybris`.
- Defining both `have_vibrator_native` and `have_vibrator_binder` silently drops
  every vibrator BuildRequires.

So a flag is switched off by deleting its line. dhd has the same trap with
`installable_zip`: it tests `%if 0%{?installable_zip:1}`
(droid-hal-device.inc:663-667), so `%define installable_zip 0` still switches
it on.

| macro | value | evidence |
|---|---|---|
| `device` | pdx246 | user decision (DEVICE=pdx246 everywhere); `~/.hadk.env` DEVICE=pdx246 |
| `vendor` | sony | user decision; the target name `sony-pdx246-aarch64` = $VENDOR-$DEVICE-$PORT_ARCH (util.sh:342) |
| `vendor_pretty` / `device_pretty` | Sony / Xperia 10 VI | user decision; they become hw-release `NAME="Sony Xperia 10 VI"` and `PRETTY_NAME="Xperia 10 VI 0.0.1.<build>"` (dhv:139, :145; seen in the rpmspec -P output) |
| `have_vibrator_native` | 1 | see 3.1 |
| `have_led` | 1 | see 3.2 |

Deliberately not defined:

| macro | why not |
|---|---|
| `rpm_device`, `rpm_vendor` | the defaults (= device, vendor) are what is wanted (dhv:19-24) |
| `have_vibrator_binder` | needs `ngfd-plugin-binder-vibrator`. No public source repo was found (GitHub repository search for "binder-vibrator" and "ngfd-plugin vibrator": none from mer-hybris/sailfishos; sailfishos/ngfd has only ffmemless). It is not in the 5.1.0.11 adaptation-common repo (its primary.xml was fetched and read; no ngfd package at all). Defining it next to native would also cancel both (dhv:84, :89). It stays as a fallback that needs one line changed (see TODO R3). |
| `have_vibrator` | the libhybris path (ngfd-plugin-droid-vibrator + qt5-feedback-haptics-droid-vibrator, dhv:93-97) via the legacy `vibrator.default.so`, which the LineageOS build does ship in vendor/lib64/hw. It is an extra layer over the same sysfs that the native plugin drives directly. |
| `have_ffmemless` | no force-feedback input device: `# CONFIG_INPUT_QCOM_HV_HAPTICS is not set` (`$ANDROID_ROOT/out/target/product/pdx246/obj/KERNEL_OBJ/.config:2729`, kernel 5.10.269-gki-ga6ce50fc4d00; parrot_GKI.config:81; the LineageOS build has the same setting); the motor is the LED-class LDO device |
| `have_kernel_modules` | only adds `BuildRequires: droid-hal-kernel-modules` to the build root (dhv:71-73); it changes nothing in the image. The LVM boot route keeps kernel-modules out of droid-config's pattern, so that `build_packages.sh -i` makes a `mic create loop` image (dhd build_packages.sh:410-427); img-boot carries the modules. |
| `have_droid_bin` | no droid-bin package exists in this port (system stays in super) |
| `native_build` | for builds without droid-hal; not this port |
| `home_url` | left at the .inc default `"https://sailfishos.org/"` (dhv:26-28). Whether to point HOME_URL at the port's own page is a user choice (TODO B4). |
| `_obs_build_project` | OBS only; local builds take the `droid-hal-kernel` branch (dhv:65-74) |
| `installable_zip` | a dhd macro, not a dhv one; it must stay undefined in droid-hal-pdx246 (see above) |

### 3.1 Vibrator: `have_vibrator_native 1` (ngfd-plugin-native-vibrator)

- pdx246's vibrator is the PM7250B LDO motor. The DT node is `pm7250b_vib:
  qcom,vibrator@5300 { compatible = "qcom,qpnp-vibrator-ldo"; ... }`
  (sm6450-devicetrees@958dce5 qcom/pm7250b.dtsi:417-421). The device boots the
  parrot-qrd overlay with PM7250B (sm6450-devicetrees README.md). The module is
  `leds-qpnp-vibrator-ldo.ko` (device/sony/pdx246 vendor_dlkm.modules.load:156),
  built as `CONFIG_LEDS_QPNP_VIBRATOR_LDO=m`
  (`$ANDROID_ROOT/out/target/product/pdx246/obj/KERNEL_OBJ/.config:5004`).
- The driver registers a plain LED-class device named `vibrator`
  (kernel/sony/sm6450 drivers/leds/leds-qpnp-vibrator-ldo.c:364-368,
  brightness_set at :285-306, plus a `vmax_mv` attribute at :237-238). The
  `duration`/`activate`/`state` files come from the transient trigger, which is
  built in (`CONFIG_LEDS_TRIGGER_TRANSIENT=y`, gki_defconfig:518 and
  KERNEL_OBJ/.config:5022).
- The trigger is selected by the vendor init file that ships with the AIDL HAL:
  vendor/qcom/opensource/vibrator@ff107c4
  aidl/vendor.qti.hardware.vibrator.service.rc:6-7
  (`on late-init` / `write /sys/class/leds/vibrator/trigger "transient"`). The
  HAL is in PRODUCT_PACKAGES (device/sony/pdx246 device.mk:350-354), its rc is in
  the LineageOS vendor image
  (`<lineageos tree>/out/target/product/pdx246/vendor/etc/init/`; the hybris
  build does not produce it), and it declares `android.hardware.vibrator` AIDL
  v2 (aidl/vendor.qti.hardware.vibrator.service.xml:31). Sailfish keeps
  LineageOS's vendor partition, so droid-hal-init parses this rc. The HAL itself
  uses the same files: VibratorOL/Vibrator.cpp:80 `LED_DEVICE
  "/sys/class/leds/vibrator"`, :395-413 (open `activate`).
- ngfd-plugin-native-vibrator (mer-hybris/ngfd-plugin-droid-vibrator,
  rpm/ngfd-plugin-native-vibrator.spec, 1.4.2, `-DNATIVE_VIBRATOR=ON`) probes, in
  order: configured paths, `/sys/class/timed_output/vibrator/enable`,
  `/sys/class/leds/vibrator/{duration,activate,state}`, then
  `{duration,activate}`. It does not write the trigger (src/native.c, read on
  GitHub). The generic udev rule hands those three files to system:input 0664
  on add|change of any LED device (droid-hal-configs
  sparse/lib/udev/rules.d/998-droid-system.rules:18-21). Selecting a trigger
  sends a change uevent, so the rule runs again once the files exist (kernel
  behaviour, inferred; see TODO R1).
- Precedent: the Xperia 10 IV/10 V port runs the same combination. The sm6375
  kernel uses the same driver (`CONFIG_LEDS_QPNP_VIBRATOR_LDO=m`,
  `<sfos>/pdx235/android_kernel_sony_sm6375`
  arch/arm64/configs/vendor/holi_GKI.config:165). The 10 V runs the same QTI
  AIDL HAL (vendor.qti.hardware.vibrator.service.xml in
  `<sfos>/pdx235/sailfish-on-zambezi/Notes.md:159`). Its droid-hal-version sets
  `have_vibrator_native 1`, and droid-config-pdx235 commit f989c8b is titled
  "Display, wifi, vibr, LED working". That droid-config does not disable
  vendor.qti.vibrator: its disabled_services.rc:25 names only the generic
  vendor.vibrator-1-0.
- The upstream pattern template already requires the native plugin
  (patterns-sailfish-device-adaptation-@DEVICE@.inc:22-24, 1dae7f2), and so does
  the 10 V pattern (patterns-sailfish-device-adaptation-xqdc72.inc:47-48).

### 3.2 LED: `have_led 1`

- In dhv, `have_led` only adds `BuildRequires: mce-plugin-libhybris` (dhv:55-58),
  so the plugin is recorded in the build root and package list
  (`extended-packagelist-droid`, dhv:155). The image requires
  mce-plugin-libhybris regardless, through the pattern (template :49-50,
  "This is needed for notification LEDs"), and `--mw` builds it in its default
  set (build_packages.sh:282). The define therefore cannot break the image. It
  only states that the port has a notification LED.
- pdx246 has an RGB notification LED at `/sys/class/leds/{red,green,blue}`
  (device/sony/pdx246 device.mk:174-179: the LineageOS AIDL lights HAL "keeps
  the RGB notification LED (/sys/class/leds/{red,green,blue})"). The
  `leds-aw2016.ko` and `leds-qti-tri-led.ko` modules are loaded
  (vendor_dlkm.modules.load:153-154), but the DT sources do not show which one
  drives it.
- The lights HAL is AIDL (`android.hardware.light-service.lineage`), so it is
  NOT the path: mce-plugin-libhybris drives LEDs through its own sysfs backends.
  The plugin's tree has sysfs-led-{vanilla,redgreen,white,binary,...}.c. The
  vanilla backend uses `RedDirectory=/sys/class/leds/red` and so on
  (inifiles/60-vanilla.ini). Without a configured backend it probes hammerhead,
  htcvision, bacon, f5121, vanilla, redgreen, white, binary, mind2v1, mind2v2
  (sysfs-led-main.c). Choosing the backend is droid-config's job (an mce ini),
  not this repo's.

## 4. BuildRequires the -v step needs (parsed with rpmspec, no OBS)

The spec parsed cleanly, with no warnings:

    Requires: patterns-sailfish-device-configuration-pdx246
    BuildRequires: droid-hal droid-config droid-config-sailfish libhybris
      mce-plugin-libhybris droid-hal-kernel droid-config-preinit-plugins
      pulseaudio-modules-droid droid-config-pulseaudio-settings
      ngfd-plugin-native-vibrator hybris-libsensorfw-qt5
      qt5-qpa-hwcomposer-plugin qtscenegraph-adaptation

| needed | comes from |
|---|---|
| droid-hal, droid-hal-kernel | `-d` (dhd Provides at droid-hal-device.inc:204, :272) |
| droid-config, -sailfish, -preinit-plugins, -pulseaudio-settings, and patterns-sailfish-device-configuration-pdx246 (runtime) | `-c` (droid-configs.inc Provides at :72, :195, :169, :177; patterns/patterns-sailfish-device-configuration-pdx246.inc in droid-config-pdx246) |
| libhybris, pulseaudio-modules-droid, mce-plugin-libhybris, qt5-qpa-hwcomposer-plugin | `--mw` default set (build_packages.sh:272-283), with pulseaudio-modules-droid kept at 14.2.106 (README.md). `.repo/manifest.xml` has no `hybris/mw` entries (checked: the file itself only includes default.xml, which the grep at :233 does not follow; default.xml and the three local manifests name no hybris/mw either), so the default set is used (manifest lookup :213-222, test :232-233). |
| hybris-libsensorfw-qt5 | the port's sensorfw binder build, `--mw=https://github.com/sailfishos/sensorfw --spec=rpm/sensorfw-qt5-binder.spec` (0.15.2; its spec has `Provides: hybris-libsensorfw-qt5`). adaptation-common 5.1.0.11 also has hybris-libsensorfw-qt5-binder 0.15.1 with the same Provides, which would satisfy this BuildRequires, but droid-config's pattern requires >= 0.15.2. |
| qtscenegraph-adaptation | adaptation-common 5.1.0.11 (0.8.1) |
| ngfd-plugin-native-vibrator | NOT in adaptation-common 5.1.0.11. It is presumably in Jolla's own repo, because the 10 IV/10 V README lists every extra `--mw` build and this plugin is not among them (inferred). See TODO B1. |

The port's build order (the same in every adaptation repo):

1. Host, in `$ANDROID_ROOT` with `PORT_ARCH=aarch64` exported, after `lunch lineage_pdx246-bp4a-userdebug`:
   `make hybris-hal droidmedia vendor_dlkmimage audio.hidl_compat.default`.
2. Platform SDK, from `$ANDROID_ROOT`, all with `rpm/dhd/helpers/build_packages.sh`:
   `-d` → `-c` → `-o --mw` (after checking out pulseaudio-modules-droid 14.2.106) →
   `--mw=https://github.com/sailfish-on-nabu/parse-android-dynparts` →
   `--mw=https://github.com/sailfishos/sensorfw --spec=rpm/sensorfw-qt5-binder.spec` → `-g` →
   `-o -N --mw=droid-hal-img-boot-pdx246` → `-v` → `-i`.

img-boot is built through `--mw`, not `-b`, because only buildmw runs dhd's
img-boot preparation (util.sh:278-298): it removes the installed img-boot from
the target and reinstalls droid-hal-pdx246-kernel and -kernel-modules. mb2's
`--output-dir` implies `--search-output-dir`, so every build also updates the
target from droid-local-repo, and an old img-boot (which Provides and
Obsoletes droid-hal-pdx246-kernel-modules) can replace -kernel-modules after a
`-d` rebuild; img-boot's build then finds no kernel-modules package. `-o`
skips buildmw's `git pull` (util.sh:262-265) and `-N` its tag check
(util.sh:268-271; the img-boot repo is untagged so that Version stays the
kernel version).

`-v` itself needs none of the img-boot packages (dhv:66-74 takes the
`droid-hal-kernel` branch outside OBS). It only needs `-d`, `-c`, the default
`--mw` set, the sensorfw build and ngfd-plugin-native-vibrator.

## 5. Cross-repo contract

- Submodule pins across the port: dhd be67bbc (droid-hal-pdx246), droid-hal-configs
  1dae7f2 (droid-config-pdx246), droid-hal-version 09c2745 (this repo),
  hybris-initrd 7b972b6 (droid-hal-img-boot-pdx246).
- droid-config-pdx246 must use `rpm_device` = `pdx246` (by default, `device pdx246`).
  ssu maps hw-release's MER_HA_DEVICE through `[hwrelease.device] %DEVICE%=%DEVICE%`
  to the board-mapping section `[pdx246]` (droid-hal-configs
  ssu/board-mappings.d/05-sfe.ini.in:1-2, installed by droid-configs.inc:476-482).
  Its `device_pretty`/`vendor_pretty` should equal this spec's ("Xperia 10 VI", "Sony").
  Its community board mapping (`10-community.ini`) needs the section `[pdx246]`.
- droid-config-pdx246 must build `patterns-sailfish-device-configuration-pdx246`
  (dhv:43), and its adaptation pattern must keep
  `Requires: droid-hal-version-pdx246`,
  `Requires: ngfd-plugin-native-vibrator`, `Requires: libngf-qt5-qtfeedback`
  and `Requires: mce-plugin-libhybris`.
- droid-config-pdx246: do not disable `vendor.qti.vibrator` without care.
  Disabling the service through disabled_services.rc would leave its
  `on late-init` trigger write in place (only the service is redefined), but the
  reference left the service running, and that is the tested setup. See TODO R1
  for a udev fallback that sets the trigger itself.
- droid-hal-pdx246.spec (not this spec) carries `droid_target_aarch64 1`.
- The repo checkout path is `$ANDROID_ROOT/hybris/droid-hal-version-pdx246`
  (two levels deep, exactly one copy under `hybris/`), with the submodule at
  `droid-hal-version`.
- `~/.hadk.env`: VENDOR=sony, DEVICE=pdx246 and PORT_ARCH=aarch64 give the mb2
  target `sony-pdx246-aarch64`. `HABUILD_DEVICE=pdx246` is set there too; it
  equals DEVICE and buildversion does not use it.

## 6. TODOs

### Runtime (on the phone, after the first Sailfish boot)

- **R1 vibrator trigger timing.** `vendor.modprobe` is started (not exec'd) on
  early-init (vendor init.qti.kernel.rc:34-35, `class main`, `oneshot`), and
  leds-qpnp-vibrator-ldo.ko is entry 156 of vendor_dlkm.modules.load. If the
  module is not yet loaded when the late-init write runs, the trigger stays
  `none`, the three files do not exist, and the native plugin finds no backend.
  Check: `cat /sys/class/leds/vibrator/trigger` shows `[transient]`;
  `ls -l /sys/class/leds/vibrator/{duration,activate,state}` shows system:input
  rw-rw-r--; as root, `echo 200 > .../duration; echo 1 > .../activate` buzzes.
  If the trigger is missing, the fix belongs in droid-config, not here: a udev
  rule `ACTION=="add", SUBSYSTEM=="leds", KERNEL=="vibrator", ATTR{trigger}="transient"`
  (selecting the trigger re-fires the change event, so the chown rules then run).
- **R2 ngfd uses the plugin.** Check `systemctl --user status ngfd` and its
  journal for the droid-vibrator plugin, and that haptic feedback works on a key
  press, a notification and the incoming-call pattern. If the session user cannot
  write the files (group `input`), that is again a droid-config/udev matter.
- **R3 fallback, only if native fails for a reason R1 cannot fix.** Switch to the
  binder plugin: replace the `have_vibrator_native` line with
  `have_vibrator_binder 1` (never both, see section 3), and get
  ngfd-plugin-binder-vibrator from somewhere. Its source has not been located; ask
  in #sailfishos-porters. This would also need vendor.qti.vibrator to keep
  running.
- **R4 LED.** Confirm `/sys/class/leds/{red,green,blue}` (with max_brightness,
  and blink or pattern files) and which controller drives them (aw2016 or
  qti-tri-led). That decides the mce backend in droid-config. Nothing changes
  here: `have_led` stays defined either way.
- **R5 hw-release.** On the phone: `cat /etc/hw-release` shows
  NAME="Sony Xperia 10 VI", ID=pdx246, MER_HA_DEVICE=pdx246, MER_HA_VENDOR=sony.
  `ssu s` reports the device model "Xperia 10 VI (pdx246 ...)".

### Build-time

- **B1 ngfd-plugin-native-vibrator availability.** In the Platform SDK, run
  `sdk-assistant maintain sony-pdx246-aarch64 zypper se ngfd-plugin-native-vibrator`
  (a read-only search, but it refreshes the repos over the network). If it is not
  found, build it before `-v`, as an extra step outside the standard order:
  `rpm/dhd/helpers/build_packages.sh --mw=https://github.com/mer-hybris/ngfd-plugin-droid-vibrator --spec=rpm/ngfd-plugin-native-vibrator.spec`
  (this clones the repo, so it needs a download OK). Without the plugin, `-v`
  fails on the unresolved BuildRequires.
- **B2 mb2 version fixing.** The repo has no tags, like the reference, which was
  built that way. The Version 0.0.1 comes from the .inc (dhv:31), and the
  Release is a timestamp (dhv:35-36), so every build gets a new release. If mb2
  complains about the missing tag, rerun with `-N` (`--no-fix-version`,
  build_packages.sh:86).
- **B3 after the build.** In droid-local-repo/pdx246, check that
  `rpm -qlp droid-hal-version-pdx246-0.0.1-*.aarch64.rpm` lists /usr/lib/hw-release
  and /etc/hw-release, and that `rpm -qp --requires` shows
  patterns-sailfish-device-configuration-pdx246.
- **B4 user choice.** Keep HOME_URL at sailfishos.org (the .inc default), or
  define `home_url` as the port's URL once one exists.

## 7. Provenance

| file | origin | licence handling |
|---|---|---|
| `rpm/droid-hal-version-pdx246.spec` | new. The macro names are the interface of dhv droid-hal-version.inc@09c2745, and the layout follows dhv droid-hal-version-@DEVICE@.spec.template@09c2745 (define device/vendor/pretty names/have_* flags, then `%include`); no template comment text was copied. sharks-dev's specs (no licence) were read for comparison and not copied. | in-file `SPDX-FileCopyrightText: Johannes Meyer zum Alten Borgloh` + `SPDX-License-Identifier: BSD-3-Clause` (`#` comments, no `%` in comments; Apache-2.0 until 2026-10-11, see below). **For review:** if you count the template structure as a derivative, the alternative is a REUSE.toml annotation that also names `Jolla Ltd.` (no year); the licence is the template's BSD now either way. The template has no notice of its own to keep. |
| `.gitignore` | new (BSD-3-Clause). Its two entries, `documentation.list` and `RPMS/`, are file names mb2 leaves in the repo; Jolla's droid-config repos ignore the same two names (with `installroot/` and `tmp/`, e.g. mer-hybris/droid-config-sony-zambezi@70a3767 .gitignore), and the sharks-dev reference committed its `documentation.list` instead. File names only, no text taken. | in-file SPDX header |
| `README.md`, `NOTES.md`, `SUBMODULES.md` | new | REUSE.toml annotation, CC-BY-SA-4.0 (no header, the same convention as device/sony/pdx246) |
| `REUSE.toml` | new | in-file SPDX header |
| `LICENSES/BSD-3-Clause.txt`, `LICENSES/CC-BY-SA-4.0.txt` | licence texts in the form `reuse download` writes them, copied from the LineageOS 23.2 tree (`packages/apps/Aperture/LICENSES/BSD-3-Clause.txt`, identical to SPDX's text; `packages/apps/Twelve/LICENSES/CC-BY-SA-4.0.txt`) | licence texts; REUSE convention |
| `.gitmodules` (generated by `git submodule add`) | generated | REUSE.toml annotation, BSD-3-Clause |
| `droid-hal-version/` (submodule) | mer-hybris/droid-hal-version@09c2745f7cd0eb5f5b941e97272914b03a9cadf2 | upstream's, unmodified and not copied into this repo. RPM `License: BSD` (dhv:39); no LICENSE file upstream (the GitHub license API returns 404). reuse lint skips submodules by default. |

Licences (changed 2026-10-11, the user's decision: each repository takes the
licence of the official code it builds on): the files written for this port are
BSD-3-Clause like droid-hal-version (they were Apache-2.0 before), the
documentation is CC-BY-SA-4.0.

Nothing in this repo is credited to LineageOS. "LineageOS" here always means
this device's own LineageOS 23.2 build (its vendor partition and out/ tree).

## 8. Sources consulted beyond the local trees

- GitHub API: mer-hybris/droid-hal-version commits (head = 09c2745); the
  mer-hybris/ngfd-plugin-droid-vibrator tree, src/native.c and
  rpm/ngfd-plugin-native-vibrator.spec; the mer-hybris/mce-plugin-libhybris tree,
  inifiles/60-vanilla.ini and sysfs-led-main.c; sailfishos/sensorfw
  rpm/sensorfw-qt5-binder.spec; the sailfishos/ngfd tree; repository searches for
  the binder vibrator plugin.
- releases.jolla.com 5.1.0.11 jolla-hw/adaptation-common/aarch64 repomd.xml and
  primary.xml.gz (11 KB of repo metadata, fetched to list the package names).
- #sailfishos-porters, 2026-07-12: the recommendation to keep
  pulseaudio-modules-droid at 14.2.106 (commit 65edd31f) for Sailfish OS 5.1.
