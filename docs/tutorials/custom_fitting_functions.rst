.. _custom_fitting_functions:

Step 6 - Custom Fitting Functions
===================================

.. raw:: html

    <video width="500" height="300" controls>
        <source src="../_static/custom_fitting_functions.mp4" type="video/mp4">
        Your browser does not support the video tag.
    </video>

Sometimes, the default fitting functions presented by Eddington aren’t enough for your
specific use-case and you may want to write your own fitting function instead.
In this video, you will see how to load a fitting function into Eddington-GUI and use
it to fit the data.

Here, we’ll assume you are familiar with the Python programming language and that you
read the tutorial for how to write a fitting function. You can read this tutorial in the
following URL
(https://eddington.readthedocs.io/en/latest/tutorials/writing_your_own_fitting_function.html).

Here, we wrote a fitting function in a python file called “fitting.py”. You can see
that we wrote a fitting function, wrapped with the “fitting_function” decorator,
in order to indicate that this is the actual fitting function.

Pay attention, Eddington-GUI won’t recognize a fitting function unless it is wrapped
with the “fitting_function” decorator, and that the “save” parameter is not set to
false, as described in the tutorial.

In Eddington-GUI’s main window, click the “Load module” button and find the python
module you’ve written. After you load the file, your new fitting function will be added
to the fitting functions selection box. Select it and use it as any other fitting
function.

Thank you for watching this video. In the next and final video we’ll summarize
everything we walked through in these videos
