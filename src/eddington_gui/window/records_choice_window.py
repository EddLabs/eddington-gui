"""Window for choosing record to use in fit data."""
from typing import List, Callable
import toga
from eddington import FitData
from toga.style import Pack
from toga.style.pack import COLUMN

from eddington_gui.boxes.line_box import LineBox
from eddington_gui.consts import LINE_HEIGHT, SMALL_PADDING, RECORD_WINDOW_SIZE


class RecordsChoiceWindow(toga.Window):  # pylint: disable=too-few-public-methods
    """Window for choosing which records to consider when using fit data."""

    __save_action: Callable
    __checkboxes: List[toga.Switch]

    def __init__(self, fit_data: FitData):
        """Initialize window."""
        super(RecordsChoiceWindow, self).__init__(size=RECORD_WINDOW_SIZE)
        main_box = toga.Box(style=Pack(direction=COLUMN))
        data_box = toga.Box()
        self.__checkboxes = [
            toga.Switch(
                label="",
                is_on=fit_data.is_selected(i),
                style=Pack(height=LINE_HEIGHT,),
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
            data_box.add(
                toga.Box(
                    style=Pack(
                        flex=1,
                        direction=COLUMN,
                        padding_left=SMALL_PADDING,
                        padding_right=SMALL_PADDING,
                    ),
                    children=[toga.TextInput(initial=header, id=header+",0", style=Pack(height=LINE_HEIGHT))]
                    + [  # noqa: W503
                        toga.TextInput(initial=column[j-1], id=header+","+str(j), style=Pack(height=LINE_HEIGHT))
                        for j in range(1, 1 + len(column))
                    ],
                )
            )
        main_box.add(data_box)
        main_box.add(
            LineBox(
                children=[
                    toga.Button(label="Save", on_press=self.save_action(fit_data))
                ],
            )
        )
        scroller = toga.ScrollContainer(content=main_box)
        self.content = scroller

    def change_value(self, fit_data: FitData):
        #Initially made for on_change for the TextInput holding the values of fit_data.
        #Because on_change is activated for all changes (every char added) it will get very annoying, very fast.
        #For now, nothing calls this method.
        
        def change_widget_value(widget):
            col = widget.id.split(",")[0]
            print(col)
            row = int(widget.id.split(",")[1])
            print(row)
            fit_data.set_cell(row, col, widget.value)
        
        return change_widget_value

    def save_action(self, fit_data: FitData):
        """Save selected records to fit data."""

        def save(widget):  # pylint: disable=unused-argument
            for i in range(fit_data.length):
                if self.__checkboxes[i].is_on:
                    fit_data.select_record(i + 1)
                else:
                    fit_data.unselect_record(i + 1)
            self.close()

        return save
