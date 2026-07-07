# EPSON Projector test

Minimum required Home Assistant version is: 2026.6.0

## About

This is a custom integration that lives next to the standard Home Assistant [EPSON integration](https://www.home-assistant.io/integrations/epson/). It's main purpose is to figure out what is needed to get LS11000 working and test out changes/concepts for the underlying epson-projector library.

Disable the standard Epson entry if you want to connect to the same projector from the Epson Test integration.

DO NOT USE THIS FOR A PRODUCTION SYSTEM!

Backward compatibility not guarenteed.

## Goal

The initial goal is to:

* Make it possible to add LS11000 to Home Assistant
* Add a lamp hours sensor
* Add a remote entity to be able to use the arrow keys, menu, enter, default, esc buttons from my UC Remote 2 (universal remote that can talk to Home Assistant)

Potential later steps (not in this PoC)

* Make CMode a select entity
* Use Data Update Coordinator for polling
* Add more sources
* Make Mute state aware (it now sends the Mute key which presumably toggles mute)
* Capability detection/selection, to avoid exposing/polling things that are not supported. Could be based on responses from projector, options flow or a model based capabilities table.

## Progress tracking

* Temporariliy add an option to specify custom ports to more easily work with a [projector-emulator](https://github.com/mvdwetering/epson-projector-tools).
* Added ESC/VP.net support (it is selectable, untested yet)
* Error message 401 from Epson = Authorization required --> No password support
* Added password support against `test_1` branch
  * Works for both HTTP and ESC/VP.net
* Next hurdle is serial number. LS11000 does not support the EasyMP serial number method on port 3620
  * Both HTTP and ESC/VP.net fail on this
  * Need alternative to `get_serial_number`
  * Implemented `get_serial_number_alt` which uses SNO command under the hood. This works, projector now can be added to HA
* Noticed that the serial number is not checked at integration setup, only during configflow to avoid setting up duplicates. I could connect to a different model in the emulator which has a different serial number. Maybe that is intended because retrieving serial number seems to have added later? But still if it has a serial number and reads a different one that should be detected !?
* I would have expected that a volume slider would show up in the mediaplayer when connecting to a(n emulated) projector with VOL support over http. But no volume indicator shows up, still only the +/- buttons and mute.
  * There were 2 issues here
    * The number that comes back from projector is 0-255 and was only made a float, but HA wants number in range 0.0-1.0 so it seems to silently ignore when out of range
    * Also the `MediaPlayerEntityFeature.VOLUME_SET` feature needs to be set before the slider shows up. It seems that readonly volume is not supported?
  * After fixing these issues the volume slider shows up and updates when reading changed values from the projector. But...
    * Setting volume is not implemented and results in an error message.
    * The +/- volume buttons disappeared. I think they used to always be there, but they are hidden since the recent-ish UI rework for mediaplayer card when volume setting is available.

## Downloading

### Home Assistant Community Store (HACS)

> HACS is a third-party downloader for Home Assistant to easily install and update custom integrations made by the community. See <https://hacs.xyz/> for more details.

You can add this repository to HACS on your Home Assistant instance with the button below.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mvdwetering&repository=epson_test&category=integration)

If the button does not work, or you don't want to use it, follow these steps to add the integration to HACS manually.

<details>
<summary>Manual HACS configuration steps</summary>

- Go to your Home Assistant instance
- Open the HACS page
- Add this repository as a custom repo through the ⋮ menu as type "Integration"
- Search for "EPSON Projector test" and click it
- Press the Download button and wait for it to download
- **Restart Home Assistant**

</details>

### Manual download

- Go to the [releases section on GitHub](https://github.com/mvdwetering/epson_test/releases)
- Download the zip file for the version you want to install
- Extract the zip
- Ensure the `config/custom_components/epson` directory exists (create it if needed)
- Copy the files from the zip into the `config/custom_components/epson` directory
- **Restart Home Assistant**
