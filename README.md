# ios-ui-exerciser
UI Exerciser for iOS Apps

## Setup

#### Step 1: Installing Appium

This can be done in 2 ways. From terminal or installing the GUI from ".dmg" app.

Here is the link for GUI:
https://github.com/appium/appium-desktop/releases/tag/v1.6.3

The terminal command is:
```
$ npm install -g appium
```

#### Step 2: Installing the Appium Python Client and other dependencies
```
$ brew install python
$ pip install Appium-Python-Client
$ pip install -U pytest
$ brew install carthage
```

#### Step 3: Prepare setup for WebDriverAgent

***For the lastest version of the Appium GUI (v1.22.3-4) the package contents and the installation steps have changed. Please refer to "Installing WebDriverAgent and the latest Appium Client on MacOS" for more information***

This step is very important in order to be able to communicate with a physical device. For testing in simulator this step in not required.

At first we need to look into this path:
```
Applications/Appium.app/Contents/Resources/app/node_modules/appium/node_modules/appium-webdriveragent 
```

Here is the app that should help us communicate with the device. After openning the "WebDriverAgent.xcodeproj" into Xcode there are a couple of modifications that should be done.

Before oppening the project into Xcode there are some commands that should be runned. The terminal commands are:
```
$ cd /Applications/Appium.app/Contents/Resources/app/node_modules/appium/node_modules/appium-webdriveragent

$ mkdir -p Resources/WebDriverAgent.bundle 

$ ./Scripts/bootstrap.sh -d
```

As we can observe from picture below we need to replace the Bundle Identifier with a unique one. This step should be done for **"WebDriverAgentLib"** and **"IntegrationApp"**. Select the team as you personal team (using personal Apple Developer Account). This modification can be done under **Signing & Capabilities** tab. Moreover, double check if under **Build Setting - Packaging - Product Bundle Identifier** the modification is visible. If not, there should also be modified.

![Image of Xcode](/assets/images/webDriverAgent.png)

The last step is to connect the iPhone to the computer and run the command:
```
$ xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'id=your iPhone UDID here' test -allowProvisioningUpdates
```

Everytime on screen appears the prompt with giving access we need to provide. Now we should be able to see the app WebDriverAgent on the phone. In order to use the app we should go into phone setting and trust us as developer.

#### Installing WebDriverAgent and the latest Appium Client (v1.22.3-4) on MacOS

Since the package contents for the Appium GUI Client have changed in the latest release, the WebDriverAgent installation steps differ.

Appium does not have a paid Apple Developer account so you have to manually sign the package using 

```
xattr -cr
```

on the downloaded file. For example, if the application is *Appium GUI Server* and you copy it into *Applications* then the command you need to run is

```
xattr -cr "/Applications/Appium Server GUI.app"
```

Afterwards you can open the Appium GUI Client. After following the steps described in Step 3 you can then run the `script.sh` WebDriverAgent install script. This will install the agent onto the physical device.

**Note: on the latest version of Appium Client there is no need to create a new directory with WebDriverAgent.bundle**

#### Step 4: Creating and running the script

At this point Appium should be running before running the script. Inside the script there are some essential characteristics that need to be provided as platform name, platform version, udid, device name and bundle ID of the app we want to test.

Running the script: 
```
$ python script.py
```


## Demo
[Here](https://drive.google.com/file/d/1dj5aM1v_g4M6NWlz2ZsaQmfoR-7GfgBB/view?usp=sharing) is a link for demo on how to test some basic actions on a real device.
