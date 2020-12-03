# README for new_iphone_script.py

## Disclaimer: This isn't by far a finished product! Use at your own risk!

### Script Description

The script gets the XML source code and starts parsing the hierarchy for
XCUIElementTypeButton elements. It then taps every buttons found and creates
a dictionary a.k.a a rough overview of the application under test.

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

After parsing the source code, the script taps the first unpressed button in the
current screen and checks for a screen change. If the screen has changed, it
requests a re-parsing of the page and breaks the current sequence.

Each screen has a time quota allocated for parsing (currently hardcoded at 20s).
After this has been exceeded, the script tries randomly tapping previously found
buttons to exit the current state. After successfully arriving in a new screen,
the sequential parsing of the XML source code is resumed.

Every time a button tap triggers a keyboard pop-up, the script uses a
quick-and-dirty function to input a random string of 8 characters 25% of the time.

### Known Issues
        1. The script sometimes tries accessing random elements from empty sequences
        due to faulty population of the dictionary in longer test runs;

        2. The script sometimes hangs after entering the Google Account settings
        screen and trying to tap a 'chevron' button;

        3. After entering a text and arriving on aa search result screen, the script
        taps the 'Google Account: <Login Name> (<google_email_address>)' several
        times;

        4. When a search results page is not fully loaded due to slow internet speed,
        a "Not found Key" error is encountered. I suspect this is due to the XML
        page source not being complete, but still need to do some investigating;

        5. The script is in dire need of code refactoring and optimisation.

### Currently Found Appium Limitations
        1. The driver_find_elements_by_class_name selector cannot be used since
        it produces false positives. This means that when a screen is presented
        on top of another, a list of buttons from both screens is returned. Further
        investigation is needed as to why;

        2. If a notification is received during tests, an "Element not found"
        error is received when trying to perform a tap, although the element name
        has been parsed from the page's XML source. I suspect this happens for the
        find_element_by_name function call;
