#!/bin/bash

cd /Applications/Appium.app/Contents/Resources/app/node_modules/appium/node_modules/appium-webdriveragent

mkdir -p Resources/WebDriverAgent.bundle

./Scripts/bootstrap.sh -d

xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=your iphone udid here. same as in script.sh' test -allowProvisioningUpdates
