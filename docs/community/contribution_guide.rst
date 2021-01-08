.. _contribution_guide:

Contribution Guide
==================

Thank you for choosing to spend your time contributing to the Eddington platform.
Contributors are the living, beating heart of any open-source project, and we really
appreciate each and every contribution made to our code-base, big or small.

Here is a relatively short guide on how to contribute code to Eddington. Please follow
the next steps carefully when making a pull request.

Step 1 – Writing Your Code
--------------------------

Like any other open-source project in Github, contribution to Eddington is done via a
`pull-request`_ (PR). Fork the desired repository, open a feature branch, and write
your code in it.

When writing code, please pay attention that you:

1. Make sure your *master* branch is `up-to-date`_ with the latest changes in the Eddington platform, and make your feature branch based upon it. This will help you avoid merge conflicts.
2. Write your code clearly, with self-explainable variables, functions and classes.
3. Reuse existing code when possible.
4. Document new functions, classes, and modules (especially if they’re public).

The code reviews you’ll receive would often address the following guidelines, as well
as any existing design issues.

Step 2 – Testing Your Code In Development Mode
----------------------------------------------

While at the moment Eddington-GUI does not have unit tests, you can still run it in
development environment in order to test the new feature you've been added.

In order to do so, follow the following steps:

1. Create a `virtual environment`_ in order to isolate your working space from outside dependencies that can affect Eddington-GUI.
2. Install `Briefcase`_ using :code:`pip install briefcase`
3. Run Eddington-GUI in dev mode using :code:`briefcase dev`

.. note::

    Running :code:`briefcase dev` will install automatically the required dependencies
    for Eddington-GUI. If you wish to install this dependencies without running the
    program, use :code:`briefcase dev --no-run`

Step 3 – Cleaning Your Code
---------------------------

Writing a working code can sometimes be really hard, but writing a **clean** code is always
harder.

Here on the Eddington platform we believe that code should be clean, and we want to
make sure that writing clean code is as easy as possible. We do that by using automatic
tools that would help you achieve that along the way.

We use state-of-the-art static code analysis tools such as *black*, *flake8*, *pylint*,
*mypy*, *pydocstyle*, etc. Statue_ is orchestrating all these tools by running each of
them on all of our code-base.

In order to use *Statue*, follow the next steps:

1. Run :code:`pip install statue`.
2. Run :code:`statue install`. If needed, this command will install missing packages.
3. Go to the main repository directory and run :code:`statue run --context format`. This will change your code to fit styling guidelines. Save the changes in a commit or append them to an existing commit.
4. Run :code:`statue run` again (now without any arguments) and it will check if there are any issues that it wasn't able to solve on its own. If there are any errors, fix them.
5. Save all changes in a commit or append them to an existing commit.

You may find some of the errors presented by those tools tedious or irrelevant,
but rest assured that we take those errors seriously.

If you think that in a specific line an error should be ignored (using :code:`# noqa`
or :code:`# pylint: disable` for example), please make sure that this skip is justified
before applying it.


Step 4 - Testing Your Code in Production Mode
---------------------------------------------

In order to make sure that your code works in production mode, follow the following
steps:

1. Run :code:`briefcase create`. This command will create a production environment for Eddington-GUI
2. Run :code:`briefcase run`. This command will run Eddington-GUI in production mode.

.. note::

    Once you did these too steps once, you can use :code:`briefcase update` to re-install
    your code and :code:`briefcase update -d` to reinstall dependencies. After yout do
    that, run :code:`briefcase run` again to re-run Eddington-GUI.

Step 5 – Adding Yourself to the Acknowledgment File
----------------------------------------------------

We acknowledge each and every one of our contributors in *docs/acknowledgment.rst*.
Add your name to the contributors file, keeping alphabetical order.


Step 6 – Receiving a Code Review and Merging
---------------------------------------------

Push the branch and open a PR. We will make our best efforts to review your PR as soon
as possible.

Once you receive a code-review, address the issues presented to you by changing the
code or commenting back. Once all the issues are resolved, your PR will be merged to
master!

.. _pull-request: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests
.. _up-to-date: https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork
.. _virtual environment: https://docs.python.org/3/tutorial/venv.html
.. _Briefcase: https://briefcase.readthedocs.io/en/latest/
.. _tox: https://tox.readthedocs.io/en/latest/
.. _Statue: https://github.com/saroad2/statue
