"""Window for choosing record to use in fit data."""
from typing import Callable, List

import toga
from eddington import FitData
from eddington.exceptions import FitDataInvalidSyntax, FitDataColumnAlreadyExists
from toga.style import Pack
from toga.style.pack import COLUMN
import csv

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LINE_HEIGHT, RECORD_WINDOW_SIZE, SMALL_PADDING


class RecordsChoiceWindow(toga.Window):  # pylint: disable=too-few-public-methods
    """Window for choosing which records to consider when using fit data."""

    __save_action: Callable
    __checkboxes: List[toga.Switch]
    __fit_data_copy: FitData

    def __init__(self, fit_data: FitData):
        """Initialize window."""
        super().__init__(size=RECORD_WINDOW_SIZE)
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        self.__fit_data_copy = FitData(fit_data.data)
        self.__cols = {}
        self.__checkboxes = [
            toga.Switch(
                label="", is_on=fit_data.is_selected(i), style=Pack(height=LINE_HEIGHT)
            )
            for i in range(1, fit_data.length + 1)
        ]
        data_box.add(
            toga.Box(
                style=Pack(
                    flex=1,
                    direction=COLUMN,
                    padding_left=SMALL_PADDING,
                    padding_right=SMALL_PADDING,
                ),
                children=[toga.Label(text="Chosen", style=Pack(height=LINE_HEIGHT))]
                + self.__checkboxes,  # noqa: W503
            )
        )
        for header, column in fit_data.data.items():
            self.__cols[header] = header
            data_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[toga.TextInput(initial=header, id=header+",0", style=Pack(height=LINE_HEIGHT), on_change=self.change_value_action(self.__fit_data_copy))]
                    + [  # noqa: W503
                        toga.TextInput(initial=column[j-1], id=header+","+str(j), style=Pack(height=LINE_HEIGHT), on_change=self.change_value_action(self.__fit_data_copy))
                        for j in range(1, 1 + len(column))
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Save selections",
                                on_press=self.save_action(fit_data,
                                                          self.__fit_data_copy)
                                ),
                    toga.Button(label="Save changes to file",
                                on_press=self.save_to_file_action(
                                    self.__fit_data_copy)
                                ),
                    toga.Button(label="Update data and save changes to file",
                                on_press=self.save_to_file_and_update_action(
                                    fit_data,
                                    self.__fit_data_copy)
                                ),
                ],
            )
        )
        scroller = toga.ScrollContainer(content=main_box)
        self.content = scroller

    def change_value_action(self, fit_data: FitData):
        # Initially made for on_change for the TextInput holding the values of
        # fit_data.
        # Because on_change is activated for all changes (every char added) it
        # will get very annoying, very fast.
        # For now, on_change is used.
        
        def change_value(widget):
            col = self.__cols[widget.id.split(",")[0]]
            row = int(widget.id.split(",")[1])
            if row != 0:
                try:
                    fit_data.set_cell(row, col, widget.value)
                except FitDataInvalidSyntax as error:
                    self.error_dialog(
                        title="Invalid input!", message=str(error),
                    )
                    widget.value = fit_data.data[col][row-1]
            else:
                try:
                    fit_data.set_header(col, widget.value)
                    self.__cols[widget.id.split(",")[0]] = widget.value
                except FitDataColumnAlreadyExists as error:
                    self.error_dialog(
                        title="Header name is already in use!",
                        message=str(error),
                    )
                    widget.value = col
        
        return change_value

    @classmethod
    def inner_save(self, fit_data: FitData, fit_data_copy: FitData):
        columns = fit_data.all_columns
        for i in range(fit_data.length):
            if self.__checkboxes[i].is_on:
                fit_data.select_record(i + 1)
            else:
                fit_data.unselect_record(i + 1)
            for column in columns:
                if (fit_data.data[column][i] != fit_data_copy.data[column][i]):
                    fit_data.set_cell(i, column, fit_data_copy.data[column][i])

    def save_action(self, fit_data: FitData, fit_data_copy: FitData):
        """Save selected records to fit data."""

        def save(widget):  # pylint: disable=unused-argument
            self.inner_save(fit_data, fit_data_copy)
            self.close()

        return save

    @classmethod
    def inner_save_changes(self, fit_data: FitData):
        # We only want to save the checked rows

        save_file_path = self.save_file_dialog("Save changes to:",
                                               "data_changes.csv")
        # TODO: make suggested_filename same as the name of the input file.
        with open(save_file_path, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            columns = fit_data.all_columns
            writer.writerow(columns)
            for i in range(fit_data.length):
                # only save the checked rows,
                # but do not change the state of fit_data.
                if self.__checkboxes[i].is_on:
                    row = [fit_data.data[column][i] for column in columns]
                    writer.writerow(row)       

    def save_to_file_action(self, fit_data: FitData):
        """
        Save changes to a new file.
        """

        def save_to_file(widget):
            self.inner_save_changes(fit_data)

        return save_to_file

    def save_to_file_and_update_action(self, fit_data: FitData, 
                                       fit_data_copy: FitData):
        """
        Save changes to a new file and update fit_data.
        """

        def save_to_file_and_update(widget):
            self.inner_save_changes(fit_data)
            self.inner_save(fit_data, fit_data_copy)
            self.close()

        return save_to_file_and_update
