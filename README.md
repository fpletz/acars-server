# ACARS Server

This projects aims to implement an ACARS service for flight simulation purposes. In the real world, ACARS is a digital datalink system for transmission of short messages between aircraft and ground stations.

The goal is to reimplement the functionality of [Hoppie's ACARS](https://www.hoppie.nl/acars/) and provide a more modern and scalable replacement. The old Hoppie API will still be supported and requests are proxied to Hoppie as required.

Existing ACARS clients should be able to change the URL and still be able to work and talk to other clients connected to either the original Hoppie network or directly to this service.

## Current State

* [x] Parsing to and from the old Hoppie API
* [x] Proxy requests to Hoppie
* [ ] File Uploads using DATAREQ
  * is this really needed?
* [ ] INFOREQ support instead of proxying
* [ ] PING for ALL-CALLSIGNS locally
* [ ] Message database
* [ ] Design new and modern API
  * [ ] Long Polling
  * [ ] Websockets
* [ ] HTML interface to inspect online stations and message history
* [ ] Login (Vatsim SSO?)
* [ ] Support different networks (Vatsim, ICAO)

## Starting the service

```
$ poetry run acars-server
```
