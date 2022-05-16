#!/bin/bash

UDID="id=<iPhone_UDID>"

xcodebuild -project "/Applications/Appium Server GUI.app/Contents/Resources/app/node_modules/appium/node_modules/appium-webdriveragent/WebDriverAgent.xcodeproj" -scheme WebDriverAgentRunner -destination $UDID test -allowProvisioningUpdates
