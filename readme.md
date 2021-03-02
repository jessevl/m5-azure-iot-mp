# Azure IoT Hub for MicroPython

Many small microcontrollers can run MicroPython nowadays, which speeds up development of proof of concepts greatly compared to using C/C++ or Arduino code. Unfortunately, Azure IoT Hub does not provide a MicroPython compatible SDK as the standard Python SDK is too big for cheap microcontrollers such as the ESP32 and incompatible.

This project is a first attempt at wrapping the functions nescessary to communicate with Azure IoT Hub in a basic and light-weight library. It is currently a work in progress and only sending telemetry is functional (although direct methods/c2d msg/device twins are in the works). The library will need a connection string and will calculate the derived SAS token like the official SDK, it does not need a pre-calculated SAS token.

This library is only tested with the M5Stack Core 2 and UIFlow firmware (which is MP), but will likely work on any MP device with wifi as most dependencies are included. In the future a sample for the M5Stack Core 2 including a touch screen UI using LVGL will be added, and the IoT Hub library itself will be split into a seperate repo.

