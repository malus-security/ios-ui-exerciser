# README for new_iphone_script.py

## Disclaimer: This isn't by far a finished product! Use at your own risk!

### Script Description

The script gets the XML source code and starts parsing the hierarchy for
XCUIElementTypeButton elements. It then taps every buttons found and creates
a dictionary a.k.a a rough overview of the application under test.

The script selects an interest class to get all the elements from an application's
page. It then sequentially goes through each of them and tries tapping, taking
into account screen changes. The current goal is to go through as many screens
s possible and to create a dictionary, a rough overview of the application under test.

The dictionary structure is as follows:

```
screens : {
        'screen_hash' : {
                'buttons' : [],
                'next_buttons' : [(presssed_button, placeholder)]
        }
}
```

The script is currently configured to test the iOS Google Chrome App, but after
refining, it should be able to test any application.

**buttons** is a list of all the buttons from a screen, while next_buttons is a list
of only the buttons that trigger a screen change.

To test for a screen change, the script stores the md5 hash of screen's XML source
code and after a button press it checks it against the hash of the current screen.

**next_buttons** is a list of all the buttons from a screen that have triggered
a screen change. The idea was to use this to get out of a situation where we have
no new buttons to press, but due to limitations of hashing XML source code for
a unique identifier, screens that look the same to a human, the script sees as
different. This leads to screens with identical *buttons* and *next_buttons* list
and reaches a loop.

*placeholder* is currently just a 0, in the future this should be filled with the
screen we arrived in.
***
### Script Logic

***Before running the script I recommend turning on do not disturb mode!***  
Check known issues as to why.

The script selects one *interest class* (e.g. XCUIElementTypeButton) to get
elements of using Appium's `find_elements_by_class_name` function.

Then script taps the first unpressed button in the current interest list and
checks for a screen change. A screen change is detected if there is a change in
the elements of the current interest list. If the screen has changed, it requests
a re-parsing of the page and breaks the current sequence.

Each screen has a time quota allocated for parsing (currently hardcoded at 20s).
After this has been exceeded, the script tries randomly tapping an element of a
previously unvisited interest list to exit the current state. After successfully
arriving in a new screen, the sequential tapping of elements is resumed.

After finishing trying to tap elements from one interest list, the script selects
another random unvisited one.

Every time a button tap triggers a keyboard pop-up, the script uses a
quick-and-dirty function to input a random string of 8 characters 25% of the time.

### Known Issues
        1. The script sometimes tries accessing random elements from empty sequences
        due to faulty population of the dictionary in longer test runs;

        2. The screen change detection needs improving, since it currently produces
        false positives;

        3. The script sometimes hangs after entering the Google Account settings
        screen and trying to tap a 'chevron' button;

        4. When a search results page is not fully loaded due to slow internet speed,
        a "Not found Key" error is encountered. I suspect this is due to the XML
        page source not being complete, but still need to do some investigating;

        5. The script sometimes hangs when the Appium Server calls interfere with
        the time checking if statement;

        5. The script is in dire need of optimisation in terms of calls made to
        The Appium server.

### Currently Found Appium Limitations
        1. The driver_find_elements_by_class_name selector produces false positives.
        This means that when a screen is presented on top of another, a list of
        buttons from both screens is returned. Further investigation is needed as to why;

        2. If a notification is received during tests, an "Element not found"
        error is received when trying to perform a tap, although the element name
        has been parsed from the page's XML source. I suspect this happens for the
        find_element_by_name function call;

        3. Some buttons get assigned a new WevDriver Element id each time they are tapped;

        4. (Google Chrome Specific) If Voice search is used after the script passes
        the element existence check, and the page then reloads, an "element not found"
        error is received;

        5. Sometimes unknown server error exceptions are reported by the Selenium WebDriver.
