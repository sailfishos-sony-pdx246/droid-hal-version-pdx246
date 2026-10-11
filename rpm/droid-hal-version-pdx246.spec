# SPDX-FileCopyrightText: Johannes Meyer zum Alten Borgloh
# SPDX-License-Identifier: BSD-3-Clause

# Version and hw-release package for the Sony Xperia 10 VI (pdx246), built by
# rpm/dhd/helpers/build_packages.sh -v. The packaging itself is in the
# droid-hal-version submodule (mer-hybris/droid-hal-version); this file only
# sets the macros that its .inc reads.
#
# The .inc tests whether a macro is DEFINED, never its value: a flag set to 0
# is still on. To switch a flag off, delete its line. A commented-out line must
# also lose its percent sign, because rpm expands macros inside comments too.

# One build serves both variants, XQ-ES54 and XQ-ES72, so the package carries
# the codename: droid-hal-version-pdx246. rpm_device and rpm_vendor are left to
# default to these two values. They must match droid-config-pdx246, because ssu
# maps MER_HA_DEVICE from /etc/hw-release to the board-mapping section of the
# same name that droid-config installs.
%define device pdx246
%define vendor sony

# Written into /etc/hw-release as NAME and PRETTY_NAME.
%define vendor_pretty Sony
%define device_pretty Xperia 10 VI

# Haptics: ngfd-plugin-native-vibrator, which writes duration, activate and
# state under /sys/class/leds/vibrator itself. The motor hangs off the PM7250B
# LDO (leds-qpnp-vibrator-ldo.ko registers an LED-class device named
# "vibrator"); those three files come from the kernel's transient LED trigger,
# which vendor.qti.hardware.vibrator.service.rc selects on late-init. So no
# binder or libhardware vibrator plugin is needed, and ffmemless does not apply
# because there is no force-feedback input device.
%define have_vibrator_native 1

# Notification LED: puts mce-plugin-libhybris into the build root and the
# package list. mce drives the LED through the plugin's sysfs backends, and
# droid-config chooses the backend.
%define have_led 1

%include droid-hal-version/droid-hal-version.inc
