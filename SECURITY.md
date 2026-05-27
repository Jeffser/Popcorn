# Security Policy

## Supported Packaging and Distribution Methods

Popcorn only supports [Flatpak](https://flatpak.org/) officially, any other packaging methods might not behave as expected.
Thus, official security-related support is only provided to the Flatpak distribution as of right now.
This may be subject to change in the future.

---

## Data Handling

### Library

- Any data related to the user's library, history and playback is handled by the server and thus is out of the scope of Popcorn.

### Telemetry

- Popcorn does **not** include any telemetry.

### Password

- The password needed for connecting to a server is stored securely using the library `libsecret` which handles passwords in the device's keyring.

---

## What Popcorn Will **Never** Do

- Share library information outside of server - client interactions
- Collect usage data
- Facilitate content piracy

