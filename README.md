# EPSON Projector test

Minimum required Home Assistant version is: 2026.6.0

## About

This is a custom integration that lives next to the standard Home Assistant [EPSON integration](https://www.home-assistant.io/integrations/epson/). It's main purpose is to figure out what is needed to get LS11000 working and test out changes/concepts for the underlying epson-projector library.

Disable the standard Epson entry if you want to connect to the same projector from hte Epson Test integration.

DO NOT USE THIS FOR A PRODUCTION SYSTEM!

Backward compatibility not guarenteed.

## Progress tracking

* Temporariliy add an option to specify custom ports to more easily work with a [projector-emulator](https://github.com/mvdwetering/epson-projector-tools).
* Added ESC/VP.net support (it is selectable, untested yet, keep for later)
* Error message 401 from Epson = Authorization required --> No password support


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
