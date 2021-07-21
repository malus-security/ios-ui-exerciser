# iOS UI Exerciser

The following describes the inner workings and the usage of the current version
of the UI Exerciser.

### Required Script Configurations

Before the actual testing, certain capabilities need to be set in order for the
script to correctly identify the Application Under Test (AUT) and be able to
perform actions on it.

These capabilities can be found in the **setUp** function at the beginning of
the script. The required fields are:

```
desired_capabilities={
        'platformName': 'iOS',
        'platformVersion': <iOS version on the real device>,
        'udid': <device id of the real device>,
        'deviceName': <device name of the real device>,
        'bundleId': <id of the AUT>
}
```

### User Input

Currently, the script waits for desired XCUIElementType classes as a required
parameter and allows the user to set a timeout marker and a desired similarity
threshold.

The **accepted XCUIElementType** classes are:

- XCUIElementTypeButton;
- XCUIElementTypeCell;
- XCUIElementTypeLink;
- XCUIElementTypeImage;
- XCUIElementTypeStaticText;
- XCUIElementTypeOther.

The **timeout value** is a limit for how long the script should be running. The
algorithm will end as soon as all the server operations allow, after the time
threshold has been exceeded. For example: if the time limit is 60s but the
operations take 65s to complete, the script will end after 65s.
By default, the timeout value is set to 0, meaning the script will run indefinetly
if no value is specified.

The **similarity threshold** is a float value representing the percentage two
different screens have the same XML source code. This is needed because certain
small changes in the page's code occur when interacting with buttons, changes
that do not necessarily produce visual differences.
By default, the similarity threshold is set to 0.9.

#### User Input Exemples

```
python3 UI_Exerciser.py -c XCUIElementTypeCell XCUIElementTypeImage -t 120
```

This will run the script searching for Cells and Images, for a duration of 120s,
leaving the similarity threshold to the default value.

```
python3 UI_Exerciser.py -c XCUIElementTypeCell XCUIElementTypeImage XCUIElementTypeButton -t 60 -s 0.85
```

This command will run the script searching for Cells, Images and Buttons for 60s
and with a similarity threshold of 85%.

### Script Description

A certain class of interest is then selected for the current screen, out of the
XCUIElementType classes inputted by the user. If the list received from the
Appium server contains no elements from the desired class, a new one is selected,
without the need of making another re-query request to the Appium server for the
XML page source. As soon as no more elements from any class of interest are left
to visit, the algorithm ends.

If there are available elements, however, the script begins to tap them in a
sequential matter, checking for previously visited or invisible elements. After
every event the script checks for a screen change.


```
screens : {
        'screen_hash' : {
                'buttons' : [],
                'next_buttons' : [(presssed_button, placeholder)],
                'visited_interest_classes' : [],
                'similarity_list' : {
                        'screen_hash' : 'similarity_value'
                },
                'similarity_check_performed' : False
        }
}
```

**buttons** is a list of all the buttons from a screen, while next_buttons is a list
of only the buttons that trigger a screen change.

To test for a screen change, the script stores the MD5 hash of screen's XML source
code and after a button press it checks it against the hash of the current screen.

**next_buttons** is a list of all the buttons from a screen that have triggered
a screen change. The idea was to use this to get out of a situation where we have
no new buttons to press, but due to limitations of hashing XML source code for
a unique identifier, screens that look the same to a human, the script sees as
different. This leads to screens with identical *buttons* and *next_buttons* list
and reaches a loop.

*placeholder* is a 0 for the current screen. After a screen change is detected,
the required association between button and screen is updated in the previous
screen's dictionary entry.

**similarity_list** is a dictionary containing the association between a screen
hash value and a similarity percentage, calculated upon entering a new screen.
Basically, after every screen change, the similarity value of the current screen
is computed in relation to all the previous ones and afterwards the *similarity_check_performed*
value is set to True.

**visited_interest_classes** is a list of the completely visited classes for the current
screen.

#### Script Logic

***Before running the script I recommend turning on do not disturb mode!***  
Receiving notifications can lead to mismatches when querying the list of buttons.

The script selects one *interest class* (e.g. XCUIElementTypeButton) to get
elements of using Appium's `find_elements_by_class_name` function.

Then script taps the first unpressed button in the current button list and
checks for a screen change. If a screen change happened, the relevant info is
recorded in the hashtable and the script re-queries the server for a new XML
source, in order to create a new dictionary entry. Then, the script selects a
new class of interest in order to create pseudo-randomness and the process begins
again. The similarity function is called during the re-parsing of the screen source
code. This ensures that in the event of a similarity being detected, the respective
hash keys changes are made before populating the list of buttons.

For every new screen, the script also counts the number of tapped or untapped
elements (the untapped elements being the sum of the invisible and visited ones).
If the sum of these elements is equal to the number of elements that the Appium
server returned for that particular class, then the script changes its current
class of interest and makes a request to the server for a new list of
interactable buttons.

### Known Limitations

##### Appium Server Connection Problems

There are events where the Appium Server closes its socket without warning.
This is solved closing the server window and the singleton test manager and by
disconnecting the USB cable and reconnecting the device again. In other terms,
a full reset of the testing environment solves the issue, but the current test
results will be discarded. Moreover, interrupting the script (with SIGINT) and
restarting it can sometimes produce the same socket error.

##### Exiting the AUT

Another way the script will encounter errors is if, by triggering a certain
button, the AUT leaves the foreground. This can happen, for instance,
in browsers, from clicking download links. This is expected behaviour, because
in the initial desired capabilities an app bundle id needs to be given, precisely
so that the XCode framework can query its XML source code and in turn provide
the response to the Appium’s WebDriverAgent. This will cause the Python script
to hang, and an error getting the main window is presented to the server backend.

##### User-level Errors

In its current form, the script expects the list of class arguments separated by
spaces and correctly spelled. In the event that one or more of the classes are
misspelled, the findElements function will return every element on the page and
the algorithm will continue its course.
